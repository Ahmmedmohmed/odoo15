from datetime import date

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class PettyCashRequest(models.Model):
    _name = 'petty.cash.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("waiting_cfo_approval", "Waiting CFO Approval"),
            ("waiting_ceo_approval", "Waiting CEO Approval"),
            ("approved", "Approved"),
            ("canceled", "Canceled")
        ],
        default="draft",
        tracking=True
    )
    skip_ceo_approval = fields.Boolean(
        string='Skip CEO Approval',
        tracking=True
    )
    reference = fields.Char(
        tracking=True
    )
    date = fields.Date(
        default=fields.Date.today()
    )
    journal_id = fields.Many2one(
        'account.journal',
        required=1
    )
    account_journal_ids = fields.Many2many(
        'account.journal'
    )
    petty_cash_line_ids = fields.One2many(
        'petty.cash.line',
        'petty_cash_request_id'
    )
    account_payment_records = fields.Integer(
        compute='compute_account_payment_records'
    )
    account_payment_ids = fields.Many2many(
        'account.payment',
        copy=False
    )

    def compute_account_payment_records(self):
        for rec in self:
            account_payment_records = self.env['account.payment'].search_count([
                ('id', 'in', rec.account_payment_ids.ids)
            ])
            if account_payment_records:
                rec.account_payment_records = account_payment_records
            else:
                rec.account_payment_records = 0

    def action_show_payments(self):
        action = self.env.ref('account.action_account_payments_payable').read()[0]
        if self.account_payment_records > 1:
            action['domain'] = [('id', 'in', self.account_payment_ids.ids)]
            action['context'] = False
        elif self.account_payment_records == 1:
            action['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            action['res_id'] = self.account_payment_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.constrains('account_journal_ids')
    def count_petty_cash_lines(self):
        for rec in self:
            rec.petty_cash_line_ids = False
            if rec.account_journal_ids:
                for journal in rec.account_journal_ids:
                    rec.petty_cash_line_ids += self.env['petty.cash.line'].create({
                        'petty_cash_journal_id': journal.id,
                        'petty_cash_request_id': rec.id,
                        'journal_id': rec.journal_id.id
                    })
            else:
                rec.petty_cash_line_ids = False

    def name_get(self):
        result = []
        for rec in self:
            name = 'Petty Cash Request - ' + str(rec.id)
            result.append((rec.id, name))
        return result

    def action_cfo_approved(self):
        for rec in self:
            if not rec.petty_cash_line_ids:
                raise ValidationError("You must add a petty cash journal line to confirm request !")
            if rec.account_payment_ids:
                rec.account_payment_ids = False
            for line in rec.petty_cash_line_ids:
                payment = self.env['account.payment'].create({
                    'journal_id': line.journal_id.id,
                    'destination_journal_id': line.petty_cash_journal_id.id,
                    'amount': line.amount,
                    'date': rec.date,
                    'ref': line.memo,
                    'is_internal_transfer': True,
                    'payment_type': 'outbound',
                })
                rec.account_payment_ids += payment
            if rec.skip_ceo_approval:
                rec.state = 'approved'
            else:
                rec.state = 'waiting_ceo_approval'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_ceo_approved(self):
        for rec in self:
            rec.state = 'approved'

    def action_confirm(self):
        for rec in self:
            rec.state = 'waiting_cfo_approval'

    def action_cancel(self):
        for rec in self:
            rec.state = 'canceled'
