

from odoo import fields, models, api, _


class TherapeuticReason(models.Model):

    _name = "therapeutic.reason"
    _rec_name = 'reason'

    reason = fields.Char()
