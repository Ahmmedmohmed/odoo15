""" Initialize Project """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class MaterialPurchaseRequisition(models.Model):
    _inherit = 'material.purchase.requisition'

    service_id = fields.Many2one(
        'fleet.vehicle.log.services',
        string='Service'
    )
