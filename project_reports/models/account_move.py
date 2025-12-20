# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, exceptions
from datetime import timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta


# class AccountMove(models.Model):
#     _inherit = 'account.move'
#
#     word_num = fields.Char(
#         string="Amount In Words:",
#         compute='_amount_in_word',
#         translate=True
#     )
#     current_year = fields.Char(
#         compute='_current_year'
#     )
#     wo_no = fields.Char(
#         string="WO.NO:",
#     )
#     po_no = fields.Char(
#     string="PO.NO:",
#    )
#
#
#
#
# @api.model
# def _count_with_hold(self):
#     for rec in self:
#         with_hold = []
#         if rec.invoice_line_ids:
#             for line in rec.invoice_line_ids:
#                 if line.tax_ids:
#                     for tax in line.tax_ids:
#                         if tax.name not in with_hold:
#                             with_hold += [[tax.name, -1 * line.price_subtotal / 100 * tax.amount]]
#         merged_dict = {}
#         for item in with_hold:
#             label = item[0]
#             value = item[1]
#             if label in merged_dict:
#                 merged_dict[label] += value
#             else:
#                 merged_dict[label] = value
#         merged_list = [[key, value] for key, value in merged_dict.items()]
#         return merged_list
#
#
# def _current_year(self):
#     for rec in self:
#         rec.current_year = str(datetime.now().year)
#
#
# def _amount_in_word(self):
#     for rec in self:
#         if self.env.user.lang == "ar_001":
#             rec.word_num = str(rec.currency_id.with_context(lang='ar_001').amount_to_text(rec.amount_residual))
#         else:
#             rec.word_num = str(rec.currency_id.amount_to_text(rec.amount_residual))
class AccountMove(models.Model):
    _inherit = 'account.move'

    word_num = fields.Char(
        string="Amount In Words:",
        compute='_amount_in_word',
        translate=True
    )
    current_year = fields.Char(
        compute='_current_year'
    )
    wo_no = fields.Char(
        string="WO.NO:",
    )
    po_no = fields.Char(
        string="PO.NO:",
    )

    @api.model
    def _count_with_hold(self):
        for rec in self:
            with_hold = []
            if rec.invoice_line_ids:
                for line in rec.invoice_line_ids:
                    if line.tax_ids:
                        for tax in line.tax_ids:
                            if tax.name not in with_hold:
                                with_hold += [[tax.name, -1 * line.price_subtotal / 100 * tax.amount]]
            merged_dict = {}
            for item in with_hold:
                label = item[0]
                value = item[1]
                if label in merged_dict:
                    merged_dict[label] += value
                else:
                    merged_dict[label] = value
            merged_list = [[key, value] for key, value in merged_dict.items()]
            return merged_list

    def _current_year(self):
        for rec in self:
            rec.current_year = str(datetime.now().year)

    def _amount_in_word(self):
        for rec in self:
            if self.env.user.lang == "ar_001":
                rec.word_num = str(rec.currency_id.with_context(lang='ar_001').amount_to_text(rec.amount_residual))
            else:
                rec.word_num = str(rec.currency_id.amount_to_text(rec.amount_residual))