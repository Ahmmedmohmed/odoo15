""" Initialize Project """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    odometer_unit = fields.Selection([
        ('kilometers', 'km'),
        ('miles', 'Hours')
    ], 'Odometer Unit', default='kilometers', help='Unit of the odometer ', required=True)
