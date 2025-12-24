from datetime import date

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class InsuranceFormLine(models.Model):
    _name = 'insurance.form.line'

    index = fields.Integer()
    employee_id = fields.Many2one(
        'hr.employee',
        string='اسم المؤمن عليه'
    )
    insurance_number = fields.Char(
        string='الرقم التأميني',
        related='employee_id.insurance_number'
    )
    national_id = fields.Char(
        string='الرقم القومي',
        related='employee_id.national_id'
    )
    joining_date = fields.Date(
        string='تاريخ الإلتحاق',
        related='employee_id.joining_date'
    )
    insurance_subscription_fee = fields.Float(
        string='اجر الإشتراك التأمينى',
        related='employee_id.insurance_subscription_fee'
    )
    comprehensive_wage = fields.Float(
        string='الأجر الشامل',
        related='employee_id.comprehensive_wage'
    )
    insurance_form_id = fields.Many2one(
        'insurance.form'
    )


