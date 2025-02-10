# -*- coding: utf-8 -*-
# from odoo import http


# class ControlDeDispositivos(http.Controller):
#     @http.route('/control_de_dispositivos/control_de_dispositivos', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/control_de_dispositivos/control_de_dispositivos/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('control_de_dispositivos.listing', {
#             'root': '/control_de_dispositivos/control_de_dispositivos',
#             'objects': http.request.env['control_de_dispositivos.control_de_dispositivos'].search([]),
#         })

#     @http.route('/control_de_dispositivos/control_de_dispositivos/objects/<model("control_de_dispositivos.control_de_dispositivos"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('control_de_dispositivos.object', {
#             'object': obj
#         })
