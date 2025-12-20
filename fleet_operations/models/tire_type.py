

from odoo import fields, models, api, _


class TireType(models.Model):

    _name = "tire.type"

    name = fields.Char()
