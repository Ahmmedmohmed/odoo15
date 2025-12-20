# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, exceptions
from datetime import timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    word_num = fields.Char(
        string="Amount In Words:",
        compute='_amount_in_word',
        translate=True
    )
    check_number= fields.Char()

    def _amount_in_word(self):
        for rec in self:
            if self.env.user.lang == "ar_001":
                rec.word_num = str(rec.currency_id.with_context(lang='ar_001').amount_to_text(rec.amount))
            else:
                rec.word_num = str(rec.currency_id.amount_to_text(rec.amount))
