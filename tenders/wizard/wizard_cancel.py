from odoo import models, fields, api


class WizardCancel(models.TransientModel):
    _name = 'wizard.cancel'
    _description = 'Wizard Cancel'

    reason_of_cancel = fields.Char(
        string="Reason",
        required=True
    )
    tender_request_id = fields.Many2one(
        'tender.request'
    )

    @api.model
    def default_get(self, default_fields):
        res = super(WizardCancel, self).default_get(default_fields)
        tender_request = self.env['tender.request'].browse(self.env.context.get('active_ids'))
        if tender_request:
            res.update({
                'tender_request_id': tender_request.id
            })
        return res

    def button_send(self):
        self.tender_request_id.write({'state': 'cancel',
                                      'reason_of_cancel': self.reason_of_cancel})
