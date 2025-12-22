from datetime import date

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class InsuranceForm(models.Model):
    _name = 'insurance.form'

    office = fields.Char(
        string='مكتب'
    )
    facility_number = fields.Char(
        string='رقم المنشأة'
    )
    start_date = fields.Date()
    facility_name = fields.Char(
        string='إسم المنشأة'
    )
    manager = fields.Char(
        string='المالك / المدير المسؤول'
    )
    establishment = fields.Char(
        string='الشكل القانونى للمنشأة'
    )
    address = fields.Char(
        string='عنوان المنشأة'
    )
    street = fields.Char(
        string='اسم الشارع'
    )
    village = fields.Char(
        string='الشياخة / القرية'
    )
    department = fields.Char(
        string='القسم / المركز'
    )
    city = fields.Char(
        string='المحافظة'
    )
    patient_insurance_percentage = fields.Char(
        string='نسبة تأمين المريض'
    )
    percentage_start_date = fields.Date(
        string='تاريخ بدأ النسبة'
    )
    injury_insurance_percentage = fields.Char(
        string='نسبة تأمين الإصابة'
    )
    second_percentage_start_date = fields.Date(
        string='تاريخ بدأ النسبة'
    )
    stop_date = fields.Date(
        string='تاريخ التوقف / الإستمرار'
    )
    stop_reason = fields.Char(
        string='سبب التوقف'
    )
    activity_start = fields.Char(
        string='بدأ النشاط'
    )
    tax = fields.Char(
        string='رقم التسجيل الضربيى للمنشاة'
    )
    insurance_form_line_id = fields.One2many(
        'insurance.form.line',
        'insurance_form_id'
    )
    total_insurance_subscription_fee = fields.Float(
        string='مجموع اجر الإشتراك التأمينى',
        compute='compute_total'
    )
    total_comprehensive_wage = fields.Float(
        string='مجموع الأجر الشامل',
        compute='compute_total'
    )
    reported_name = fields.Char(
        string='أقر أنا'
    )
    manager_reported_name = fields.Char(
        string='بصفتي'
    )
    employees_number = fields.Char(
        string='بأن إجمالى أعداد المؤمن عليهم'
    )
    current_money = fields.Float(
        string='وأن أجور الشهر الحالى'
    )
    manager_signature = fields.Char(
        string='توقيع صاحب العمل أو المدير المسئول'
    )
    receiver = fields.Char(
        string='مستلم الإستمارة'
    )
    same_signature = fields.Char(
        string='تم مطابقة التوقيع بمعرفتى'
    )
    specialist = fields.Char(
        string='أخصائى الإشتراك'
    )
    register = fields.Char(
        string='سجل آلياً'
    )
    review = fields.Char(
        string='روجع آلياً'
    )
    end_date = fields.Date(
        string='تحريراً فى'
    )

    def name_get(self):
        result = []
        for rec in self:
            name = 'نموذج' + ' ' + str(rec.id)
            result.append((rec.id, name))
        return result

    def compute_total(self):
        for rec in self:
            rec.total_insurance_subscription_fee = 0
            rec.total_comprehensive_wage = 0
            if rec.insurance_form_line_id:
                rec.total_insurance_subscription_fee = sum(
                    line.insurance_subscription_fee for line in rec.insurance_form_line_id)
                rec.total_comprehensive_wage = sum(line.comprehensive_wage for line in rec.insurance_form_line_id)
