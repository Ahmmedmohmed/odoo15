# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    insurance_number = fields.Char(
        string='الرقم التأميني'
    )
    national_id = fields.Char(
        string='الرقم القومي'
    )
    joining_date = fields.Date(
        string='تاريخ الإلتحاق'
    )
    insurance_subscription_fee = fields.Float(
        string='اجر الإشتراك التأمينى'
    )
    comprehensive_wage = fields.Float(
        string='الأجر الشامل'
    )
    birth_date = fields.Date(
        string='تاريخ الميلاد'
    )
    age = fields.Integer(
        compute='_compute_age',
        store=True,
        string='العمر'
    )
    bank_1 = fields.Many2one(
        'bank.bank',
        string='Bank 1'
    )
    account_number_1 = fields.Char(
        string='Account Number 1'
    )
    bank_2 = fields.Many2one(
        'bank.bank',
        string='Bank 2'
    )
    account_number_2 = fields.Char(
        string='Account Number 2'
    )
    expiration_date = fields.Date()

    @api.depends('birth_date')
    def _compute_age(self):
        for rec in self:
            if rec.birth_date:
                today = fields.Date.today()
                age = today.year - rec.birth_date.year - ((today.month, today.day) < (rec.birth_date.month, rec.birth_date.day))
                rec.age = age
            else:
                rec.age = 0
