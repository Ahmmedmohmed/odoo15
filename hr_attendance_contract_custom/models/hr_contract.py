# -*- coding: utf-8 -*-
from odoo import models, fields


class HrContract(models.Model):
    _inherit = 'hr.contract'  # تم التصحيح من hr.version إلى hr.contract
    _description = 'Employee Contract'

    att_policy_id = fields.Many2one('hr.attendance.policy', string='Attendance Policy')
    allowances = fields.Monetary(
        string='Allowances',
        required=False,
        tracking=True,
        default=0.0,
        help="Employee's monthly allowances."
    )
    insurance_salary = fields.Monetary('Insurance Salary', required=False, tracking=True)

    def _compute_employee_taxes(self, contract_id, tax_base=0):
        # تم التصحيح لاستخدام hr.contract
        contract_obj = self.env['hr.contract'].sudo().search([('id', '=', contract_id)])

        # ... (باقي الكود كما هو بدون تغيير في الحسابات) ...

        monthly_gross_income = (
                contract_obj.insurance_salary + contract_obj.allowances) if contract_obj.insurance_salary > 0 else (
                contract_obj.wage + contract_obj.allowances)

        # ... (أكمل باقي الدالة كما هي لديك) ...

        return [0, 0, 0]  # (اختصاراً هنا، اترك الحسابات كما هي في ملفك الأصلي)

    def init(self):
        super().init()
        # تم التصحيح لجدول hr_contract
        self.env.cr.execute("""
            UPDATE hr_contract
               SET allowances = 0
             WHERE allowances IS NULL
        """)