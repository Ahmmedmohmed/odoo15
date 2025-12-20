# Copyright 2016 Tecnativa - Carlos Dauden
# Copyright 2018 ACSONE SA/NV.
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    # We keep this field for migration purpose
    old_contract_id = fields.Many2one("contract.contract")
    contract_id = fields.Many2one("contract.contract")
    project_id = fields.Many2one(
        'project.project'
    )

    def x_action_post(self):
        res = super(AccountMove, self).action_post()
        for rec in self:
            for line in rec.invoice_line_ids:
                if line.contract_line_id:
                    contract_line = line.contract_line_id
                    act_line = (line.price_subtotal / contract_line.price_subtotal) * 100
                    contract_line.sudo().write({
                        'achievement_pre': act_line,
                        'invoice_subtotal': line.price_subtotal
                    })
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    contract_line_id = fields.Many2one(
        "contract.line", string="Contract Line", index=True
    )
