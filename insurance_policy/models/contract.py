# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ContractApps(models.Model):
    _inherit = "contract.contract"

    def create_insurance_policy(self):
        print('=========== TEST ===============')
        self.ensure_one()
        insurance_policy_obj = self.env['insurance.policy'].sudo()
        val = {}
        for rec in self:
            if rec.partner_id:
                val['customer_id'] = rec.partner_id.id
            if rec.date_start:
                val['date_from'] = rec.date_start
            if rec.date_end:
                val['date_to'] = rec.date_end
            if rec.contract_value:
                val['amount'] = rec.contract_value
            if rec.code:
                val['contract_no'] = rec.code
            val['contract_id'] = self.id
        print('=========== val ===========', val)
        if val:
            insurance_policy_obj.create(val)


