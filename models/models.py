# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ControlDeDispositivos(models.Model):
    # Atributos
    _inherit = "res.partner"

    # Diccionario global con la configuración
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

    #****************************************
    # Declaracion de Dispositivos

    dispMax = fields.Integer(
        string='Máxima cantidad de dispositivos', 
        store=True, 
        readonly=False
    )

    dispTipo = fields.Selection(
        selection=[('movil', 'Móvil'),
                   ('tablet', 'Tablet'),
                   ('laptop', 'Laptop'),
                   ('otro', 'Otro')], 
        string="Tipo de Dispositivo", 
        default="movil", 
        store=True
    )

    dispTiempoPredeterminado = fields.Integer(
        string="Tiempo Predeterminado (horas)", 
        default=1, 
        readonly=True
    )
        
    producto_vinculado_id = fields.Many2one(
        'product.product',  
        string="Producto Vinculado", 
        help="Vincula este grupo de dispositivos con un producto de inventario"
    )

    @api.constrains("dispTipo")
    def _validar_tipo_dispositivo(self):
        for registro in self:
            if registro.dispTipo not in self.DISP_CONFIG['tipos_validos']:
                raise UserError(_("El tipo de dispositivo seleccionado no es válido."))


    @api.onchange("dispTipo")
    def _onchange_dispTipo(self):
        tiempo_predeterminado = self.DISP_CONFIG['tiempo_predeterminado']
        self.dispTiempoPredeterminado = tiempo_predeterminado.get(self.dispTipo, 1)


    def action_add_to_inventory(self):
        productos_por_tipo = self.DISP_CONFIG['productos_por_tipo']
        
        nombre_producto = productos_por_tipo.get(self.dispTipo, None)

        if nombre_producto:
            producto_existente = self.env['product.product'].search([ 
                ('name', 'ilike', f"{self.name} - {nombre_producto}")
            ], limit=1)

            if producto_existente:
                producto_existente.unlink()

            producto = self.env['product.template'].create({
                'name': f"{self.name} - {nombre_producto}",
                'type': 'product',
                'uom_id': self.env.ref('uom.product_uom_unit').id,
                'list_price': 150.0,
            })

            producto_producto = self.env['product.product'].search([
                ('product_tmpl_id', '=', producto.id)
            ], limit=1)

            if not producto_producto:
                producto_producto = self.env['product.product'].create({
                    'product_tmpl_id': producto.id,
                })

            location = self.env.ref('stock.stock_location_stock')

            stock_quant = self.env['stock.quant'].search([
                ('product_id', '=', producto_producto.id),
                ('location_id', '=', location.id)
            ], limit=1)

            if stock_quant:
                stock_quant.write({'quantity': self.dispMax})
            else:
                self.env['stock.quant'].create({
                    'product_id': producto_producto.id,
                    'location_id': location.id,
                    'quantity': self.dispMax,
                })

            self.producto_vinculado_id = producto_producto

            producto_producto.write({'list_price': 150.0})


    #********************************************************
    # Gestion de Dispositivos 

    dispTiempo = fields.Integer(
        string="Tiempo total faltante (horas)", 
        compute="_calcular_dispTiempo", 
        store=True
    )

    producto_vinculado_qty = fields.Float(
        string="Cantidad Disponible",
        related="producto_vinculado_id.qty_available",
        readonly=True,
        store=True
    )

    dispTiempoPredeterminadoTipo = fields.Integer(
        string="Tiempo Predeterminado del tipo (horas)", 
        default=1, 
        readonly=True
    )

    @api.depends("producto_vinculado_id", "producto_vinculado_id.name")
    def _calcular_dispTiempo(self):
        for registro in self:
            if registro.producto_vinculado_id:
                # Obtener el tipo del producto a partir del nombre
                tipo_producto = None
                nombre_producto = registro.producto_vinculado_id.name.split(' - ')[-1].lower()

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
