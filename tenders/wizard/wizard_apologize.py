from odoo import models, fields, api


class WizardApologize(models.TransientModel):
    _name = 'wizard.apologize'
    _description = 'Wizard Apologize'

    reason_of_apologize = fields.Char(
        string="Reason",
        required=True
    )
    tender_request_id = fields.Many2one(
        'tender.request'
    )

    @api.model
    def default_get(self, default_fields):
        res = super(WizardApologize, self).default_get(default_fields)
        tender_request = self.env['tender.request'].browse(self.env.context.get('active_ids'))
        if tender_request:
            res.update({
                'tender_request_id': tender_request.id
            })
        return res

    def button_send(self):
        self.tender_request_id.write({'state': 'apologize',
                                      'reason_of_apologize': self.reason_of_apologize})
