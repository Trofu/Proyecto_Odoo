# -*- coding: utf-8 -*-
{
    'name': "Control de Dispositivos",

    'summary': """
        Módulo para gestionar la actualización de dispositivos y controlar el estado de cada uno.
    """,

    'description': """
        Este módulo permite gestionar a los clientes (empresas) y el estado de los dispositivos que han sido actualizados a un nuevo software. Los dispositivos se organizan según su estado (pendiente, actualizado, en revisión, error) y se pueden asignar técnicos para su seguimiento.
    """,

    'author': "Juan Luis Espinosa Cuenca",
    'website': "https://github.com/Trofu",

    'category': 'Uncategorized',  
    'version': '0.1',


    'depends': ['base'],

    'data': [
        'security/ir.model.access.csv',  
        'views/views.xml',               
        'views/templates.xml',           
    ],

    'demo': [
        'demo/demo.xml',
    ],
}

