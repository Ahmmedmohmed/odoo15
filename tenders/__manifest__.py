{
    'name': 'Payment Tenders',
    'author': 'Amr Yasser | Secure Tech',
    'depends': [
        'base', 'mail', 'account', 'contract'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/tender_request_views.xml',
        'wizard/payment_receipt_wizard.xml',
        'wizard/wizard_not_a_word.xml',
        'wizard/wizard_cancel.xml',
        'wizard/wizard_apologize.xml',
    ],
}