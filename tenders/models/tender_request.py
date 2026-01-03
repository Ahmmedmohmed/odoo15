from odoo import models, fields, api


class TenderRequest(models.Model):
    _name = 'tender.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    code = fields.Char(string="Tender Code", readonly=True)
    customer = fields.Many2one('res.partner', string='Customer')
    project_name = fields.Char('Project Name', required=True)
    date = fields.Date('Date', required=True)
    tender_number = fields.Char('Tender Number', required=True)
    tender_amount = fields.Float('Tender Amount', required=True)
    payment_number = fields.Char('Payment number', required=True)
    bid_from = fields.Date('Bid from', required=True)
    bid_to = fields.Date('Bid to', required=True)
    attachment = fields.Binary('Attachment', required=True)
    payment_receipt = fields.Binary("Payment Receipt")
    payment_ids = fields.One2many('account.payment', 'tender_request_id', string='Payments')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('approve_cfo', 'Approved (CFO)'),
        ('reject', 'Rejected'),
        ('edit', 'To Be Edited'),
        ('cancel', 'Canceled'),
        ('approve_accountant', 'Payed and Approved (Accountant)')
    ], readonly=True, default='draft', track_visibility='onchange')

    def action_submit(self):
        self.write({'state': 'under_review'})

    def action_approve_cfo(self):
        self.write({'state': 'approve_cfo'})

    def action_reject(self):
        self.write({'state': 'reject'})

    def action_edit(self):
        self.write({'state': 'edit'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_pay(self):
        view = self.env.ref('tenders.view_payment_receipt_wizard_form')
        return {
            'name': 'Payment Receipt',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'payment.receipt.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': {
                'default_tender_request_id': self.id,
            },
        }

    def action_view_payments(self):
        self.ensure_one()
        return {
            'name': 'Payments',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'domain': [('id', 'in', self.payment_ids.ids)],
            'context': {'create': False},
        }

    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('tender.request.sequence') or '/'
        return super(TenderRequest, self).create(vals)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    tender_request_id = fields.Many2one('tender.request', string='Tender Request', ondelete='cascade')
