{
    'name': 'Insurance Form 2',
    'summary': 'Insurance Form 2',
    'author': 'Abdelrahman Ragab',
    'version': '15.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'reports/hr_employee_badge.xml',
        'views/hr_employee.xml',
        'views/insurance_form.xml',
        'views/bank.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
