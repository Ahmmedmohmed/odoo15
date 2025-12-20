# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _


class BatteryType(models.Model):

    _name = "battery.type"

    name = fields.Char()
