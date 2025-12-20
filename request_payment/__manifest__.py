# -*- coding: utf-8 -*-
{
    'name': "Request Payment",
    'summary': "Request Payment",
    'author': "Abdelrahman Ragab",
    'version': '15.0.0.1.0',
    'category': 'others',
    'license': 'AGPL-3',
    'sequence': 1,
    'depends': [
        'base',
        'mail',
        'account',
        'contract',
    ],
    'data': [
        'security/ir.model.access.csv',
        # 'views/customer_payment.xml',
        'views/vendor_payment.xml',
        'views/journal_account_payment.xml',
        'views/petty_cash_request.xml',
        'views/account_journal.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
