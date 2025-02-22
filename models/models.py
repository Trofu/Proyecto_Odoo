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
    
    dispActu = fields.Integer(
        string='Cantidad actual de dispositivos', 
        store=True, 
        readonly=True
    )

    dispRest = fields.Integer(
        string='Resto de dispositivos', 
        readonly=True, 
        compute="_dispRestantes"
    )

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

    @api.depends("dispMax", "dispActu")
    def _dispRestantes(self):
        for registro in self:
            max_disp = registro.dispMax or 0
            actu_disp = registro.dispActu or 0
            registro.dispRest = max_disp - actu_disp

    @api.onchange("dispMax")
    def _onchange_dispMax(self):
        if self.dispMax < self.dispActu:
            self.dispActu = self.dispMax
            return {
                'warning': {
                    'title': _("Ajuste Automático"),
                    'message': _("La cantidad actual de dispositivos ha sido ajustada al nuevo máximo. La cantidad actual ahora es %d." % self.dispActu),
                }
            }




    @api.depends("dispMax", "dispActu", "dispTiempoPredeterminado")
    def _calcular_dispTiempo(self):
        for registro in self:
            registro.dispTiempo = (registro.dispMax - registro.dispActu) * registro.dispTiempoPredeterminado

    def action_increase_dispActu(self):
        for record in self:
            if record.dispActu < record.dispMax:
                record.dispActu += 1
                if record.producto_vinculado_id:
                    record.producto_vinculado_id.qty_available += 1  
            else:
                raise UserError("No puedes superar el límite de dispositivos.")

    def action_decrease_dispActu(self):
        for record in self:
            if record.dispActu > 0:
                record.dispActu -= 1
                if record.producto_vinculado_id:
                    # Asegúrate de que el producto no tenga un stock negativo
                    if record.producto_vinculado_id.qty_available > 0:
                        record.producto_vinculado_id.write({
                            'qty_available': record.producto_vinculado_id.qty_available - 1
                        })
                    else:
                        raise UserError("No hay suficiente stock en el inventario para reducir los dispositivos.")
            else:
                raise UserError("No puedes tener una cantidad negativa de dispositivos.")
