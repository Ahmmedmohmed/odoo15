from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class CustomerPayment(models.Model):
    _name = "customer.payment"

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("posted", "Posted"),
            ("canceled", "Canceled")
        ],
        default="draft"
    )
    reference = fields.Char()
    payment_type = fields.Selection(
        selection=[("inbound", "Receive")],
        default="inbound",
        required=1
    )
    date = fields.Date(
        default=fields.Date.today()
    )
    customer_payment_line_ids = fields.One2many(
        'customer.payment.line',
        'customer_payment_id'
    )
    account_payment_ids = fields.Many2many(
        'account.payment'
    )
    account_payment_records = fields.Integer(
        compute='compute_account_payment_records'
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
        action = self.env.ref('account.action_account_payments').read()[0]
        if self.account_payment_records > 1:
            action['domain'] = [('id', 'in', self.account_payment_ids.ids)]
        elif self.account_payment_records == 1:
            action['views'] = [(self.env.ref('account.view_account_payment_form').id, 'form')]
            action['res_id'] = self.account_payment_ids.ids[0]
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
            if not rec.customer_payment_line_ids:
                raise ValidationError("You must add a request payment line to confirm request !")
            if rec.account_payment_ids:
                rec.account_payment_ids = False
            for line in rec.customer_payment_line_ids:
                payment = self.env['account.payment'].create({
                    'partner_type': 'customer',
                    'payment_type': rec.payment_type,
                    'date': rec.date,
                    'partner_id': line.customer_id.id,
                    'amount': line.amount,
                    'ref': line.memo,
                    'journal_id': line.journal_id.id
                })
                # payment.action_post()
                rec.account_payment_ids += payment
            rec.state = 'posted'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_cancel(self):
        for rec in self:
            rec.state = 'canceled'
