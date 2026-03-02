# -*- coding: utf-8 -*-
{
    'name': "HR Attendance Sheet And Policies (Odoo 15 Version)",

    'summary': """Managing Attendance Sheets for Employees (Downgraded to V15)""",

    'description': """
        Employees Attendance Sheet Management for Odoo 15.
        This module handles attendance policies, late in, overtime, and absence deductions.
    """,

    'author': "Ramadan Khalil",
    'website': "rkhalil1990@gmail.com",
    'price': 99,
    'currency': 'USD',

    'category': 'hr',
    'version': '15.0.1.0.0',  # تحديث الإصدار ليتوافق مع أودو 15
    'images': ['static/description/bannar.jpg'],

    'depends': [
        'base',
        'hr',
        'hr_payroll',  # يعتمد على موديول الرواتب لنسخة 15
        'hr_holidays',
        'hr_attendance',
        'resource',  # إضافة موديول الموارد لضمان عمل التقويمات
    ],
    'data': [
        'data/ir_sequence.xml',
        'data/data.xml',
        'data/ir_cron.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/change_att_data_view.xml',
        'views/hr_attendance_sheet_view.xml',  # يجب تعديل attrs في هذا الملف
        'views/hr_attendance_policy_view.xml',
        'views/hr_contract_view.xml',
        'views/hr_public_holiday_view.xml',
        'views/attendance_sheet_batch_view.xml',  # يجب تعديل attrs في هذا الملف
        'views/hr_payslip_view.xml'
    ],

    'license': 'OPL-1',
    'demo': [
        'demo/demo.xml',  # يحتوي على بيانات تجريبية للموظف رمضان خليل
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}