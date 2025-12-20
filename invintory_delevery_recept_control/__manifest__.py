# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Invintory Delevery Recept Control',
    'version': '15.0.0',
    'summary': """This module manage Invintory Delevery Recept Control.""",
    'description': """Invintory Delevery Recept Control

    """,
    'author': " A1 Infinity ERP Solutions , Mahmoud Najdy",
    'website': "https://www.a1infinity.com/",
    'category': 'Warehouse',
    'depends': [
                'stock',
                'purchase',
                'project',
                ],
    'data':[

        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/stock_picking_view.xml',
        'views/project_stock_buttons_view.xml',
        # 'views/hr_contract.xml',
        'views/fleet_vehicle_view.xml',
        'views/fleet_equpment_view.xml',
        'views/car_car_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
