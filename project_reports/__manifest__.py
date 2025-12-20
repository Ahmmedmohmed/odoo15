# -*- coding: utf-8 -*-
{
    'name': "Project Reports",
    'summary': "Project Reports",
    'author': "Abdelrahman Ragab",
    'version': '15.0.0.1.0',
    'category': 'others',
    'license': 'AGPL-3',
    'sequence': 1,
    'depends': [
        'base',
        'account',
        'contract',
    ],
    'data': [
        'views/account_payment.xml',
        'report/invoice_report.xml',
        'report/bill_report.xml',
        'report/account_payment_report.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
