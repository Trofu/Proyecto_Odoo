# -*- coding: utf-8 -*-

from odoo import models, fields, api


class control_de_dispositivos(models.Model):
    _name = 'control_de_dispositivos.control_de_dispositivos'
    _description = 'control_de_dispositivos.control_de_dispositivos'
    name = fields.Char()
    value = fields.Integer()
