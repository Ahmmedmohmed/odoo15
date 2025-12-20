from odoo import models, fields, api
from odoo.exceptions import UserError


class InheritContract(models.Model):
    _inherit = 'contract.contract'

    tender_request_id = fields.Many2one(
        'tender.request'
    )
