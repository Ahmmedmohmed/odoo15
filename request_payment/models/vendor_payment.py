from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class VendorPayment(models.Model):
    _name = "vendor.payment"
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
    payment_type = fields.Selection(
        selection=[("outbound", "Send")],
        default="outbound",
        required=1,
        tracking=True
    )
    date = fields.Date(
        default=fields.Date.today()
    )
    customer_payment_line_ids = fields.One2many(
        'customer.payment.line',
        'vendor_payment_id'
    )
    account_payment_ids = fields.Many2many(
        'account.payment',
        copy=False
    )
    account_payment_records = fields.Integer(
        compute='compute_account_payment_records'
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Vendors',
        tracking=True
    )

    @api.constrains('partner_ids')
    def count_request_payment_lines(self):
        for rec in self:
            rec.customer_payment_line_ids = False
            if rec.partner_ids:
                for partner in rec.partner_ids:
                    rec.customer_payment_line_ids += self.env['customer.payment.line'].create({
                        'customer_id': partner.id,
                        'vendor_payment_id': rec.id,
                        'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
                    })
            else:
                rec.customer_payment_line_ids = False

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

    def action_cfo_approved(self):
        for rec in self:
            if not rec.customer_payment_line_ids:
                raise ValidationError("You must add a request payment line to confirm request !")
            if rec.account_payment_ids:
                rec.account_payment_ids = False
            for line in rec.customer_payment_line_ids:
                payment = self.env['account.payment'].create({
                    'partner_type': 'supplier',
                    'payment_type': rec.payment_type,
                    'date': rec.date,
                    'partner_id': line.customer_id.id,
                    'amount': line.amount,
                    'ref': line.memo,
                    'journal_id': line.journal_id.id
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
