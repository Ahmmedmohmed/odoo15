
from odoo import fields, models, api, _


class PettyCashLine(models.Model):

    _name = "petty.cash.line"

    petty_cash_journal_id = fields.Many2one(
        'account.journal',
        required=1,
        string='Petty Cash'
    )
    balance = fields.Float(
        string='Balance',
        related='petty_cash_journal_id.default_account_id.current_balance'
    )
    required_amount = fields.Float()
    amount = fields.Float()
    journal_id = fields.Many2one(
        'account.journal',
        required=1
    )
    memo = fields.Char()
    petty_cash_request_id = fields.Many2one(
        'petty.cash.request'
    )
    project_id = fields.Many2one(
        'project.project'
    )
