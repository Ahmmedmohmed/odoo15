# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    daily_amount = fields.Float(
        string=" Daily Amount",
        compute="_compute_daily_amount",
        store=True
    )

    salary1 = fields.Monetary(
        string="Salary 1",
        currency_field='currency_id'
    )

    salary2 = fields.Monetary(
        string="Salary 2",
        currency_field='currency_id'
    )

    salary3 = fields.Monetary(
        string="Salary 3",
        currency_field='currency_id'
    )

    salary4 = fields.Monetary(
        string="Salary 4",
        currency_field='currency_id'
    )

    salary5 = fields.Monetary(
        string="Salary 5",
        currency_field='currency_id'
    )

    @api.depends('wage')
    def _compute_daily_amount(self):
        for rec in self:
            if rec.wage:
                rec.daily_amount = rec.wage / 30.0
            else:
                rec.daily_amount = 0.0


