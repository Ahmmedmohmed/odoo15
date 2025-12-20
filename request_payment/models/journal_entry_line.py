
from odoo import fields, models, api, _


class JournalEntryLine(models.Model):

    _name = "journal.entry.line"

    account_id = fields.Many2one(
        'account.account',
        string='Account',
        required=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner'
    )
    name = fields.Char(
        string='Label'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True
    )
    amount = fields.Monetary(
        'currency_id'
    )
    tax_tag_ids = fields.Many2many(
        string="Tags",
        comodel_name='account.account.tag'
    )
    amount_currency = fields.Monetary(
        currency_field='currency_id',
        string='Amount in Currency'
    )
    tax_ids = fields.Many2many(
        comodel_name='account.tax',
        string="Taxes"
    )
    tax_tag_invert = fields.Boolean(
        string="Invert Tags"
    )
    account_payment_id = fields.Many2one(
        'journal.account.payment'
    )
