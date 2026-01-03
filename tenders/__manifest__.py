{
    'name': 'Payment Tenders',
    'author': 'Amr Yasser | Secure Tech',
    'depends': [
        'base', 'mail', 'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/tender_request_views.xml',
        'wizard/payment_receipt_wizard.xml',
    ],
}