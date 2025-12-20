from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class JournalAccountPayment(models.Model):
    _name = "journal.account.payment"

    ref = fields.Char()
    date = fields.Date(
        default=fields.Date.today()
    )
    journal_id = fields.Many2one(
        'account.journal',
        required=1
    )
    journal_entry_line_ids = fields.One2many(
        'journal.entry.line',
        'account_payment_id'
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("posted", "Posted"),
            ("canceled", "Canceled")
        ],
        default="draft"
    )
    account_move_id = fields.Many2one(
        'account.move'
    )
    account_move_records = fields.Integer(
        compute='compute_account_move_records'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True
    )

    def compute_account_move_records(self):
        for rec in self:
            account_move_records = self.env['account.move'].search_count([
                ('id', '=', rec.account_move_id.id)
            ])
            if account_move_records:
                rec.account_move_records = account_move_records
            else:
                rec.account_move_records = 0

    def action_show_journal_entry(self):
        action = self.env.ref('account.action_move_journal_line').read()[0]
        if self.account_move_records == 1:
            action['views'] = [(self.env.ref('contract.view_account_move_contract_helper_form').id, 'form')]
            action['res_id'] = self.account_move_id.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def name_get(self):
        result = []
        for rec in self:
            name = 'Request Payment - ' + str(rec.id)
            result.append((rec.id, name))
        return result

    def action_post(self):
        for rec in self:
            if not rec.journal_entry_line_ids:
                raise ValidationError("You must add a journal item line to confirm request !")
            if rec.account_move_id:
                rec.account_move_id = False
            lines = []
            total_amount = 0
            for line in rec.journal_entry_line_ids:
                lines.append((0, 0, {'account_id': line.account_id.id,
                                     'partner_id': line.partner_id.id,
                                     'name': line.name,
                                     'currency_id': line.currency_id.id,
                                     'debit': line.amount,
                                     'credit': 0.0,
                                     'tax_tag_ids': line.tax_tag_ids.ids,
                                     'amount_currency': line.amount_currency,
                                     'tax_ids': line.tax_ids.ids,
                                     'tax_tag_invert': line.tax_tag_invert
                                     }))
                total_amount += line.amount
            lines.append((0, 0, {'account_id': rec.journal_id.default_account_id.id,
                                 'debit': 0.0,
                                 'credit': total_amount,
                                 }))
            move = self.env['account.move'].create({
                'move_type': 'entry',
                'ref': rec.ref,
                'date': rec.date,
                'journal_id': rec.journal_id.id,
                'currency_id': rec.currency_id.id,
                'line_ids': lines
            })
            # move.action_post()
            rec.account_move_id = move
            rec.state = 'posted'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_cancel(self):
        for rec in self:
            rec.state = 'canceled'
