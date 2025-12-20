# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo 15 Account Move Reports',
    'version': '15.0.0',
    'author': 'mahmoud Najdy , A1 ERP',
    'depends': ['account'],
    'description': """Odoo 15 Account Move Reports. """,
    'summary': 'Odoo 15 Account Move Reports',
    'category': 'Accounting',
    'sequence': -100,
    'website': 'https://www.a1infinity.com/',
    'license': 'LGPL-3',
    # 'images': ['static/description/assets.gif'],
    'data': [
        'views/account_move_views.xml',
        'report/report.xml',
    ],

    'demo': [],
    'qweb': [],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,


}
