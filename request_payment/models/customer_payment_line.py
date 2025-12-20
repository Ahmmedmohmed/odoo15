
from odoo import fields, models, api, _


class CustomerPaymentLine(models.Model):

    _name = "customer.payment.line"

    customer_id = fields.Many2one(
        'res.partner',
        required=1,
        string='Vendor'
    )
    account_id = fields.Many2one(
        'account.account',
        related='customer_id.property_account_receivable_id'
    )
    vendor_account_id = fields.Many2one(
        'account.account',
        related='customer_id.property_account_payable_id'
    )
    journal_id = fields.Many2one(
        'account.journal',
        required=1
    )
    currency_id = fields.Many2one(
        'res.currency'
    )
    amount = fields.Monetary(
        'currency_id'
    )
    balance = fields.Float(
        string='Balance',
        compute='compute_balance'
    )
    memo = fields.Char()
    customer_payment_id = fields.Many2one(
        'customer.payment'
    )
    vendor_payment_id = fields.Many2one(
        'vendor.payment'
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        'Analytic Account'
    )
    project_id = fields.Many2one(
        'project.project'
    )
    industry_id = fields.Many2one(
        'res.partner.industry'
    )

    @api.depends('customer_id')
    def compute_balance(self):
        for rec in self:
            if rec.customer_id:
                account_move_lines_balance = self.env['account.move.line'].search([
                    ('move_id.partner_id', '=', rec.customer_id.id), ('parent_state', '=', 'posted'),
                    ('full_reconcile_id', '=', False), ('balance', '!=', 0), ('account_id.reconcile', '=', True)
                ]).mapped('balance')
                rec.balance = sum(account_move_lines_balance)
            else:
                rec.balance = 0
