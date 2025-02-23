# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ControlDeDispositivos(models.Model):
    # Hereda de res.partner para extender sus funcionalidades
    _inherit = "res.partner"

    # Diccionario global con la configuración de los dispositivos
    DISP_CONFIG = {
        'productos_por_tipo': {
            'movil': 'Producto Móvil',
            'tablet': 'Producto Tablet',
            'laptop': 'Producto Laptop',
            'otro': 'Producto Otro',
        },
        'tiempo_predeterminado': {
            'movil': 1,
            'tablet': 2,
            'laptop': 3,
            'otro': 1
        },
        'tipos_validos': ['movil', 'tablet', 'laptop', 'otro']
    }

    # ****************************************
    # Declaración de Campos de Dispositivos

    # Cantidad máxima de dispositivos
    dispMax = fields.Integer(
        string='Máxima cantidad de dispositivos', 
        store=True, 
        readonly=False
    )

    # Tipo de dispositivo (movil, tablet, laptop, otro)
    dispTipo = fields.Selection(
        selection=[('movil', 'Móvil'),
                   ('tablet', 'Tablet'),
                   ('laptop', 'Laptop'),
                   ('otro', 'Otro')], 
        string="Tipo de Dispositivo", 
        default="movil", 
        store=True
    )

    # Tiempo predeterminado en horas según el tipo de dispositivo
    dispTiempoPredeterminado = fields.Integer(
        string="Tiempo Predeterminado (horas)", 
        default=1, 
        readonly=True
    )
        
    # Relación con el producto en inventario
    producto_vinculado_id = fields.Many2one(
        'product.product',  
        string="Producto Vinculado", 
        help="Vincula este grupo de dispositivos con un producto de inventario"
    )

    # **********************************
    # Validadores y Métodos Onchange

    @api.constrains("dispTipo")
    def _validar_tipo_dispositivo(self):
        # Valida que el tipo de dispositivo seleccionado sea uno de los permitidos.
        for registro in self:
            if registro.dispTipo not in self.DISP_CONFIG['tipos_validos']:
                raise UserError(_("El tipo de dispositivo seleccionado no es válido."))

    @api.onchange("dispTipo")
    def _onchange_dispTipo(self):
        # Actualiza el tiempo predeterminado según el tipo de dispositivo seleccionado.
        tiempo_predeterminado = self.DISP_CONFIG['tiempo_predeterminado']
        self.dispTiempoPredeterminado = tiempo_predeterminado.get(self.dispTipo, 1)

    @api.onchange('dispMax')
    def _onchange_cantMax(self):
        # Previene que la cantidad máxima de dispositivos sea negativa.
        if self.dispMax < 0:
            self.dispMax = 0
            return {
                'warning': {
                    'title': 'Valor no permitido',
                    'message': 'La cantidad máxima no puede ser negativa.',
                }
            }
        
    # ***************************************************
    # Método para añadir el producto al inventario

    def action_add_to_inventory(self):
        #Crea un producto en el inventario basado en el tipo de dispositivo y lo vincula.
        #Si el producto ya existe, lo elimina y crea uno nuevo con la cantidad definida.
        #productos_por_tipo = self.DISP_CONFIG['productos_por_tipo']
        
        # Obtener el nombre del producto según el tipo de dispositivo
        nombre_producto = productos_por_tipo.get(self.dispTipo, None)

        if nombre_producto:
            # Buscar si ya existe un producto con ese nombre en el inventario
            producto_existente = self.env['product.product'].search([ 
                ('name', 'ilike', f"{self.name} - {nombre_producto}")
            ], limit=1)

            # Si existe, eliminarlo para evitar duplicados
            if producto_existente:
                producto_existente.unlink()

            # Crear un nuevo template de producto
            producto = self.env['product.template'].create({
                'name': f"{self.name} - {nombre_producto}",
                'type': 'product',
                'uom_id': self.env.ref('uom.product_uom_unit').id,  # Unidad de medida
                'list_price': 150.0,  # Precio de lista inicial
            })

            # Buscar si el template tiene una variante (product.product)
            producto_producto = self.env['product.product'].search([
                ('product_tmpl_id', '=', producto.id)
            ], limit=1)

            # Si no existe una variante, se crea una nueva
            if not producto_producto:
                producto_producto = self.env['product.product'].create({
                    'product_tmpl_id': producto.id,
                })

            # Obtener la ubicación del inventario
            location = self.env.ref('stock.stock_location_stock')

            # Verificar si ya hay stock del producto en esa ubicación
            stock_quant = self.env['stock.quant'].search([
                ('product_id', '=', producto_producto.id),
                ('location_id', '=', location.id)
            ], limit=1)

            # Si existe, actualizar la cantidad
            if stock_quant:
                stock_quant.write({'quantity': self.dispMax})
            else:
                # Si no existe, crear un nuevo registro de stock
                self.env['stock.quant'].create({
                    'product_id': producto_producto.id,
                    'location_id': location.id,
                    'quantity': self.dispMax,
                })

            # Vincular el producto creado con el dispositivo
            self.producto_vinculado_id = producto_producto

            # Establecer el precio en 0 para evitar sobrecostos
            producto_producto.write({'list_price': 0.0})

    # **********************************************
    # Gestión de Dispositivos

    # Tiempo total faltante en horas basado en la cantidad disponible
    dispTiempo = fields.Integer(
        string="Tiempo total faltante (horas)", 
        compute="_calcular_dispTiempo", 
        store=True
    )

    # Cantidad disponible del producto vinculado en el inventario
    producto_vinculado_qty = fields.Float(
        string="Cantidad Disponible",
        related="producto_vinculado_id.qty_available",
        readonly=True,
        store=True
    )

    # Tiempo predeterminado del tipo de dispositivo
    dispTiempoPredeterminadoTipo = fields.Integer(
        string="Tiempo Predeterminado del tipo (horas)", 
        default=1, 
        readonly=True
    )

    @api.depends("producto_vinculado_id", "producto_vinculado_id.name")
    def _calcular_dispTiempo(self):
        
        #Calcula el tiempo total faltante en base a la cantidad de dispositivos disponibles
        #y el tiempo predeterminado del tipo de dispositivo.
        
        for registro in self:
            if registro.producto_vinculado_id:
                # Obtener el tipo del producto a partir del nombre
                tipo_producto = None
                nombre_producto = registro.producto_vinculado_id.name.split(' - ')[-1].lower()

                # Buscar el tipo de dispositivo en la configuración
                for tipo, nombre in self.DISP_CONFIG['productos_por_tipo'].items():
                    if nombre.lower() == nombre_producto:
                        tipo_producto = tipo
                        break
                
                if tipo_producto:
                    # Asignar el tiempo predeterminado según el tipo de producto
                    registro.dispTiempoPredeterminadoTipo = self.DISP_CONFIG['tiempo_predeterminado'].get(tipo_producto, 1)

                    # Calcular el tiempo total faltante con base en los dispositivos disponibles
                    registro.dispTiempo = registro.producto_vinculado_qty * registro.dispTiempoPredeterminadoTipo
                else:
                    # Si no se encuentra el tipo, establecer tiempo predeterminado como 1
                    registro.dispTiempoPredeterminadoTipo = 1
                    registro.dispTiempo = registro.producto_vinculado_qty  # Faltante sin tipo definido
            else:
                # Si no hay producto vinculado, establecer valores por defecto
                registro.dispTiempoPredeterminadoTipo = 1
                registro.dispTiempo = 0
