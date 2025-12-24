# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrEmployeeCourse(models.Model):
    _name = 'hr.employee.course'
    _description = 'Employee Training Courses'

    # ربط الكورس بالموظف
    employee_id = fields.Many2one('hr.employee', string="الموظف")

    # الحقول اللي طلبتها
    name = fields.Char(string="اسم الكورس", required=True)
    date_start = fields.Date(string="تاريخ البداية")
    date_end = fields.Date(string="تاريخ النهاية")
    location = fields.Char(string="المكان / الجهة")
    notes = fields.Text(string="ملاحظات")


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    arabic_name = fields.Char(string="Name in Arabic")
    job_position_arabic = fields.Char(string="Job Position in Arabic")
    # --- الحقول الأصلية من كودك ---
    employee_rank = fields.Char(string="Employee Rank")
    social_insurance_code = fields.Char(string="الكود التأميني")
    insurance_number = fields.Char(string='الرقم التأميني')
    national_id = fields.Char(string='الرقم القومي')
    joining_date = fields.Date(string='تاريخ الإلتحاق')
    insurance_subscription_fee = fields.Float(string='اجر الإشتراك التأمينى')
    comprehensive_wage = fields.Float(string='الأجر الشامل')
    actual_wage = fields.Float(string='الأجر الفعلى')
    birth_date = fields.Date(string='تاريخ الميلاد')
    course_ids = fields.One2many(
        'hr.employee.course',
        'employee_id',
        string="الدورات التدريبية"
    )

    age = fields.Integer(
        compute='_compute_age',
        store=True,
        string='العمر'
    )

    # تنويه: المودل الصحيح للبنوك في أودو هو res.bank
    # لو كان لديك مودل مخصص اسمه bank.bank اتركه كما هو، وإلا غيره لـ res.bank
    bank_1 = fields.Many2one('res.bank', string='Bank 1')
    account_number_1 = fields.Char(string='Account Number 1')
    bank_2 = fields.Many2one('res.bank', string='Bank 2')
    account_number_2 = fields.Char(string='Account Number 2')

    expiration_date = fields.Date(string="تاريخ الانتهاء")

    # =========================================================
    # ✅ الحقول الجديدة المضافة (حسب طلبك)
    # =========================================================

    # 1. تواريخ الشركة (الدخول والخروج)
    company_entry_date = fields.Date(string="تاريخ الدخول للشركة")
    company_exit_date = fields.Date(string="تاريخ الخروج من الشركة")

    # 2. تواريخ التأمينات الاجتماعية (الدخول والخروج)
    insurance_entry_date = fields.Date(string="تاريخ الدخول للتأمينات")
    insurance_exit_date = fields.Date(string="تاريخ الخروج من التأمينات")

    # 3. المسمى الوظيفي في التأمينات (مختلف عن المسمى الداخلي)
    insurance_job_title = fields.Char(string="المسمى الوظيفي التأميني")

    # 4. الدورات التدريبية (حقل نصي بسيط لكتابة أسماء الدورات)
    course_names = fields.Text(string="الدورات التدريبية والكورسات")

    # 5. بيانات رخصة القيادة
    driving_license_number = fields.Char(string="رقم رخصة القيادة")
    driving_license_issue_date = fields.Date(string="تاريخ إصدار الرخصة")
    driving_license_end_date = fields.Date(string="تاريخ انتهاء الرخصة")

    # 6. قيمة الاشتراك التأميني الطبي
    medical_insurance_fee = fields.Float(string="قيمة الاشتراك الطبي")

    # ---------------------------------------------------------
    # دالة حساب العمر
    # ---------------------------------------------------------
    @api.depends('birth_date')
    def _compute_age(self):
        for rec in self:
            if rec.birth_date:
                today = fields.Date.today()
                age = today.year - rec.birth_date.year - (
                            (today.month, today.day) < (rec.birth_date.month, rec.birth_date.day))
                rec.age = age
            else:
                rec.age = 0