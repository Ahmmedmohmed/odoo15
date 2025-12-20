
from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    petty_cash = fields.Boolean(
        default=False
    )
