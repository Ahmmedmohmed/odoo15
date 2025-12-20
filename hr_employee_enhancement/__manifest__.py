# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'hr_employee_enhancement',
    'version': '15.0.0',
    'summary': """Thr_employee_enhancement.""",
    'description': """hr_employee_enhancement

    """,
    'author': " A1 Infinity ERP Solutions , Mahmoud Najdy",
    'website': "https://www.a1infinity.com/",
    'category': 'hr',
    'depends': [
                'hr',
                'hr_attendance',
                'project',
                ],
    'data':[


        'views/hr_contract.xml',
        'views/hr_attendance.xml',

    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
