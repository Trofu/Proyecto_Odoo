# -*- coding: utf-8 -*-
{
    'name': "Control de Dispositivos",

    'summary': """
        Módulo para gestionar dispositivos en inventario y ver la cantidad que quedan de su propietario.
    """,

    'description': """
        Este módulo permite gestionar los dispositivos de los clientes (empresas) dentro del inventario de Odoo. 
        Se integra con el módulo de inventario para registrar y rastrear la cantidad de dispositivos disponibles. 
    """,

    'author': "Juan Luis Espinosa Cuenca",
    'website': "https://github.com/Trofu",

    'category': 'Inventory',  
    'version': '1.0',

    'depends': ['base', 'contacts', 'stock'],

    'data': [
        'views/views.xml',               
        'views/templates.xml',           
    ],

    'demo': [
        'demo/demo.xml',
    ],
}
