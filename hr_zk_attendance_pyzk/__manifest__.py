# -*- coding: utf-8 -*-
{
    'name': 'ZK Machine Integration',
    'version': '15.0.1.0.0',
    'summary': 'Integrate Biometric Devices with HR Attendance',
    'description': """
        This module integrates ZK Time & Attendance devices with Odoo 15.
        It automates the download of attendance logs and creates HR Attendance records.
    """,
    'category': 'Human Resources',
    'author': 'Rabeh MENA',
    'website': 'https://www.rabeh-mena.com',
    'depends': ['base', 'hr', 'hr_attendance', 'resource'],
    'data': [
        'security/ir.model.access.csv',
        'views/zk_machine_view.xml',  # تأكد أن هذا الملف موجود لديك
        'data/cron_job.xml',          # الملف الذي قمنا بتعديله سابقاً
    ],
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}