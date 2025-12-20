from odoo import models, fields, api


class WizardNotAWord(models.TransientModel):
    _name = 'wizard.not.a.word'
    _description = 'Wizard Not A Word'

    reason_of_not_a_word = fields.Char(
        string="Reason",
        required=True
    )
    tender_request_id = fields.Many2one(
        'tender.request'
    )

    @api.model
    def default_get(self, default_fields):
        res = super(WizardNotAWord, self).default_get(default_fields)
        tender_request = self.env['tender.request'].browse(self.env.context.get('active_ids'))
        if tender_request:
            res.update({
                'tender_request_id': tender_request.id
            })
        return res

    def button_send(self):
        self.tender_request_id.write({'state': 'not_a_word',
                                      'reason_of_not_a_word': self.reason_of_not_a_word})
