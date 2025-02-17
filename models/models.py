# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError

class control_de_dispositivos(models.Model):
    _inherit = "res.partner"
    dispMax = fields.Integer(string='dispMax',store=True, compute = "_verificarCant",readonly=False)
    dispActu = fields.Integer(string='dispActu',store=True)
    dispRest = fields.Integer(string='dispRest', readonly=True, compute="_dispRestantes")
    



    @api.depends("dispMax", "dispActu")
    def _dispRestantes(self):
        for registro in self:
            max_disp = registro.dispMax or 0
            actu_disp = registro.dispActu or 0
            registro.dispRest = max_disp - actu_disp


    @api.depends("dispMax","dispActu")
    def _verificarCant(self):
        for registro in self:
            if registro.dispActu > registro.dispMax:
                raise UserError(_("No puedes poner más dispositivos finalizados que de dispositivos totales."))
            
    
    @api.onchange("dispMax")
    def _onchange_dispMax(self):
        if self.dispMax < self.dispActu:
            self.dispActu = self.dispMax
            return {
                'warning': {
                    'title': _("Ajuste Automático"),
                    'message': _("La cantidad actual de dispositivos ha sido ajustada al nuevo máximo."),
                }
            }
        


    """dispTipo = fields.Selection([
        ('movil', 'Móvil'),
        ('tablet', 'Tablet'),
        ('laptop', 'Laptop'),
        ('otro', 'Otro')
    ], string="Tipo de Dispositivo", default="movil",store=True)

    dispTiempoPredeterminado = fields.Integer(string="Tiempo Predeterminado (horas)", default=1)
    dispTiempo = fields.Datetime(string="Tiempo de Registro", default=fields.Datetime.now)


    @api.constrains("dispTipo")
    def _validar_tipo_dispositivo(self):
        tipos_validos = ['movil', 'tablet', 'laptop', 'otro']
        for registro in self:
            if registro.dispTipo not in tipos_validos:
                raise UserError(_("El tipo de dispositivo seleccionado no es válido."))

    @api.onchange("dispTipo")
    def _onchange_dispTipo(self):
        tiempo_predeterminado = {
            'movil': 1,    # 1 hora
            'tablet': 2,   # 2 horas
            'laptop': 3,   # 3 horas
            'otro': 1      # 1 hora por defecto
        }
        self.dispTiempoPredeterminado = tiempo_predeterminado.get(self.dispTipo, 1)
        self._calcular_cantidad_por_tiempo()

        return {
            'warning': {
                'title': _("Tiempo Asignado"),
                'message': _("El tiempo predeterminado para %s es de %d horas." % (self.dispTipo, self.dispTiempoPredeterminado)),
            }
        }

    @api.onchange("dispActu")
    def _actualizar_tiempo_registro(self):
        self.dispTiempo = fields.Datetime.now()"""
