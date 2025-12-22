from datetime import date

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class BankBank(models.Model):
    _name = 'bank.bank'
    _rec_name = 'bank'

    bank = fields.Char(
        string='البنك'
    )
