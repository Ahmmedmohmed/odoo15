from odoo import fields, api, models


class LettersOfGuaranteeRequest(models.Model):
    _name = 'letters.of.guarantee.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    letter_type = fields.Selection([('primary', 'ابتدائي'), ('ultimate', 'نهائي'), ('advance_payment', 'دفعة مقدمة')],
                                   string="نوع خطاب الضمان")
    beneficiary = fields.Many2one('res.partner', string='المستفيد')
    letter_length = fields.Integer('مدة خطاب الضمان بالايام')
    project_id = fields.Many2one('project.project', 'المشروع')
    letter_purpose = fields.Char('الغرض من الخطاب (الموضوع)')
    letter_value = fields.Float('قيمة خطاب الضمان')
    state = fields.Selection([('draft', 'Draft'), ('approved_ceo', 'Approved (CEO)'), ('reject', 'Rejected')],
                             default='draft')

    def action_approve_ceo(self):
        self.ensure_one()
        self.state = 'approved_ceo'
        self.env['letters.of.guarantee'].create({
            'letter_type': self.letter_type,
            'beneficiary': self.beneficiary.id,
            'letter_length': self.letter_length,
            'purpose': self.letter_purpose,
            'project_id': self.project_id.id,
            'letter_value': self.letter_value,
            'request_id': self.id,
        })

    def action_reject(self):
        self.ensure_one()
        self.state = 'reject'

    def action_view_letters_of_guarantee(self):
        order_id = self.env['letters.of.guarantee'].sudo()
        views = [(False, 'tree'), (False, 'form')]
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'letters.of.guarantee',
                'view_mode': 'form,tree',
                'view_type': 'form',
                'res_id': order_id.id,
                'views': views,
                'target': 'current',
                'domain': [('request_id', '=', rec.id)],
            }
