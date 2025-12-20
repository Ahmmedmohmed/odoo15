""" Initialize Project """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class FleetVehicleOdometer(models.Model):
    _inherit = 'fleet.vehicle.odometer'

    project_id = fields.Many2one(
        'project.project',
        readonly=1
    )
