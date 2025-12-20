from odoo import models, fields, api


class PaymentReceiptWizard(models.TransientModel):
    _name = 'payment.receipt.wizard'
    _description = 'Payment Receipt Wizard'

    payment_receipt = fields.Binary(string="Payment Receipt", required=True)
    tender_request_id = fields.Many2one('tender.request', string="Tender Request", required=True)

    def button_approve(self):
        self.tender_request_id.write({'state': 'approve_accountant'})
        self.tender_request_id.write({'payment_receipt': self.payment_receipt})
        payment = self.env['account.payment'].create({
            'amount': self.tender_request_id.tender_amount,
            'date': self.tender_request_id.date,
            'is_internal_transfer': False,
            'payment_type': 'outbound',
            'partner_id': self.tender_request_id.customer.id,
            'tender_request_id': self.tender_request_id.id,
            'ref': self.tender_request_id.code,
        })
        return {'type': 'ir.actions.act_window_close'}
