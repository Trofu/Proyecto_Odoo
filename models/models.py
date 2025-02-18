# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ControlDeDispositivos(models.Model):
    _inherit = "res.partner"

    dispMax = fields.Integer(string='Máxima cantidad de dispositivos', store=True, compute="_verificarCant", readonly=False)
    dispActu = fields.Integer(string='Cantidad actual de dispositivos', store=True, readonly=True)
    dispRest = fields.Integer(string='Resto de dispositivos', readonly=True, compute="_dispRestantes")
    dispTipo = fields.Selection(
        selection=[('movil', 'Móvil'),('tablet', 'Tablet'),('laptop', 'Laptop'),('otro', 'Otro')], 
        string="Tipo de Dispositivo", default="movil", store=True)
    dispTiempoPredeterminado = fields.Integer(string="Tiempo Predeterminado (horas)", default=1, readonly=True)
    dispTiempo = fields.Integer(string="Tiempo total faltante (horas)", compute="_calcular_dispTiempo", store=True)

    @api.depends("dispMax", "dispActu")
    def _dispRestantes(self):
        for registro in self:
            max_disp = registro.dispMax or 0
            actu_disp = registro.dispActu or 0
            registro.dispRest = max_disp - actu_disp

    @api.constrains("dispMax", "dispActu")
    def _verificarCant(self):
        for registro in self:
            if registro.dispActu > registro.dispMax:
                raise UserError(_("No puedes poner más dispositivos actuales que el máximo permitido."))

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

    @api.constrains("dispTipo")
    def _validar_tipo_dispositivo(self):
        tipos_validos = ['movil', 'tablet', 'laptop', 'otro']
        for registro in self:
            if registro.dispTipo not in tipos_validos:
                raise UserError(_("El tipo de dispositivo seleccionado no es válido."))

    @api.onchange("dispTipo")
    def _onchange_dispTipo(self):
        tiempo_predeterminado = {
            'movil': 1,
            'tablet': 2,
            'laptop': 3,
            'otro': 1
        }
        self.dispTiempoPredeterminado = tiempo_predeterminado.get(self.dispTipo, 1)

    @api.depends("dispMax", "dispActu", "dispTiempoPredeterminado")
    def _calcular_dispTiempo(self):
        for registro in self:
            registro.dispTiempo = (registro.dispMax - registro.dispActu) * registro.dispTiempoPredeterminado

    def action_increase_dispActu(self):
        """Aumenta la cantidad actual de dispositivos."""
        for record in self:
            if record.dispActu < record.dispMax:
                record.dispActu += 1
            else:
                raise UserError("No puedes superar el límite de dispositivos.")

    def action_decrease_dispActu(self):
        """Disminuye la cantidad actual de dispositivos."""
        for record in self:
            if record.dispActu > 0:
                record.dispActu -= 1
            else:
                raise UserError("No puedes tener una cantidad negativa de dispositivos.")
