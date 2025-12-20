# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#################################################################

import base64
import io
import json
from email.quoprimime import header_decode


try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

################################################################

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


import xlsxwriter

class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_report_name = fields.Char('Account Move Report', default='دفتر مبيعات ')
    bill_report_name = fields.Char('Account Move Report', default='تسويات مشتريات ضريبة القيمة المضافة ')
    excel_sheet = fields.Binary('Download Report')

    def get_report_data(self):
        data = []
        for move in self:
            data.append({
                'month': move.invoice_date.strftime('%b %y').lower() if move.invoice_date else '',  # الشهر
                'company': move.partner_id.name or '',                                              # اسم الشركة
                'invoice_num': move.name or '',                                                     # رقم الفاتورة
                'date': move.invoice_date.strftime('%Y-%m-%d') if move.invoice_date else '',        # تاريخ الفاتورة
                'amount_untaxed_signed_without_tax': move.amount_untaxed_signed if move.amount_untaxed_signed and not move.amount_tax_signed else 0,  # اجمالي الايراد المعفي
                'amount_total_signed_without_tax': move.amount_total_signed if move.amount_total_signed and not move.amount_tax_signed else 0,  #صافي الايراد المعفي

                'amount_untaxed_signed_with_tax': move.amount_untaxed_signed if move.amount_untaxed_signed and move.amount_tax_signed else 0, # اجمالي الايراد الخاضع
                'amount_total_signed_with_tax': move.amount_total_signed if move.amount_total_signed and move.amount_tax_signed else 0, # صافي الايراد الخاضع

                'amount_total_signed': move.amount_total_signed if move.amount_total_signed else 0, # صافي الايراد الكلي

                'taxes': move.amount_tax_signed if move.amount_tax_signed else 0,  #ضريبة القيمة المضافة
                'additional_tax_value': move.invoice_line_ids.tax_ids[0].name if move.invoice_line_ids.tax_ids.ids else " ",  #نسبة ضريبة القيمة المضافة
                'address': move.partner_id.street if move.partner_id.street else " ",  # العنوان
                'tax_ref_number': move.partner_id.zip if move.partner_id.zip else " ",  # رقم التسجيل الضريبي


            })

        return data

    def action_print_excel_report(self):
        if not self:
            return

        data = self.get_report_data()
        invoice_num = len(data)
        print("invoice_num : ",invoice_num)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Invoices Report')
        worksheet.right_to_left()


        total_amount_total_signed = 0
        total_amount_total_signed_without_tax = 0
        total_amount_total_signed_with_tax = 0
        total_taxes = 0
        sequence = 0



        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'border': 1,
        })
        data_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        title_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': 'white',
            'font_size': 18,
            'bg_color': '#057dcd',
        })

        collection_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_color': 'white',
            'font_size': 16,
            'bg_color': '#000000',
            'border': 1,
            'border_color': 'white',
        })


       # REPORT TITLE
        worksheet.merge_range(0, 0, 1, 11, 'دفتر مبيعات', title_format)

        #Header

        worksheet.write(9, 0, '#', header_format)
        worksheet.write(9, 1, 'الشهر', header_format)
        worksheet.write(9, 2, 'الشركة', header_format)
        worksheet.write(9, 3, 'رقم الفاتورة', header_format)
        worksheet.write(9, 4, 'التاريخ', header_format)
        worksheet.write(9, 5, 'اجمالي الايراد المعفي', header_format)
        worksheet.write(9, 6, 'صافي الايراد المعفي', header_format)
        worksheet.write(9, 7, 'اجمالي الايراد الخاضع', header_format)
        worksheet.write(9, 8, 'صافي الايراد الخاضع', header_format)
        worksheet.write(9, 9, 'صافي الايراد الكلي', header_format)
        worksheet.write(9, 10, 'ضريبة القيمة المضافة', header_format)
        worksheet.write(9, 11, 'نسبة الضريبة', header_format)
        worksheet.write(9, 12, ' العنوان ', header_format)
        worksheet.write(9, 13, 'رقم التسجيل الضريبي ', header_format)


        row = 10
        for line in data:
            total_amount_total_signed += line['amount_total_signed']
            total_amount_total_signed_without_tax += line['amount_total_signed_without_tax']
            total_amount_total_signed_with_tax += line['amount_total_signed_with_tax']
            total_taxes += line['taxes']
            sequence+=1

        # for row, line in enumerate(data, start=10):
            worksheet.write(row, 0, sequence, data_format)
            worksheet.write(row, 1, line['month'], data_format)
            worksheet.write(row, 2, line['company'], data_format)
            worksheet.write(row, 3, line['invoice_num'], data_format)
            worksheet.write(row, 4, line['date'], data_format)
            worksheet.write(row, 5, line['amount_untaxed_signed_without_tax'], data_format)
            worksheet.write(row, 6, line['amount_total_signed_without_tax'], data_format)
            worksheet.write(row, 7, line['amount_untaxed_signed_with_tax'], data_format)
            worksheet.write(row, 8, line['amount_total_signed_with_tax'], data_format)
            worksheet.write(row, 9, line['amount_total_signed'], data_format)
            worksheet.write(row, 10, line['taxes'], data_format)
            worksheet.write(row, 11, line['additional_tax_value'], data_format)
            worksheet.write(row, 12, line['address'], data_format)
            worksheet.write(row, 13, line['tax_ref_number'], data_format)
            row += 1

        # collection of data
        worksheet.merge_range(3, 0, 3, 2, ' صافي الايراد الكلي ', collection_format)
        worksheet.write(3, 3, total_amount_total_signed, data_format)
        worksheet.merge_range(4, 0, 4, 2, ' صافي الايرادات المعفاة ', collection_format)
        worksheet.write(4, 3, total_amount_total_signed_without_tax, data_format)
        worksheet.merge_range(5, 0, 5, 2, ' صافي الايرادات الخاضعة ', collection_format)
        worksheet.write(5, 3, total_amount_total_signed_with_tax, data_format)
        worksheet.merge_range(6, 0, 6, 2, 'ضريبة القيمة المضافة ', collection_format)
        worksheet.write(6, 3, total_taxes, data_format)
        worksheet.merge_range(7, 0, 7, 2, ' عدد الفواتير المصدرة ', collection_format)
        worksheet.write(7, 3, sequence, data_format)

        workbook.close()
        output.seek(0)

        # Save the generated file to a binary field for the first record
        # You can decide what to do here, I save it to the first record's excel_sheet
        self.excel_sheet = base64.encodebytes(output.read())
        self.invoice_report_name = 'Account Move Report.xlsx'

        # Return an action to download the file of the first record to avoid singalong error
        return {
            'type': 'ir.actions.act_url',
            'name': 'Invoice Excel Report',
            'url': f'/web/content/account.move/{self[0].id}/excel_sheet/{self[0].invoice_report_name}?download=true',
            'target': 'self',
        }

    def get_bill_report_data(self):
        data = []
        for bill in self:
            tax_totals = json.loads(bill.tax_totals_json)

            data.append({
                'month': bill.invoice_date.strftime('%b %y').lower() if bill.invoice_date else '',  # الشهر
                'company': bill.partner_id.name or '',  # اسم الشركة
                'industry': bill.partner_id.industry_id.name or '',  # اسم الشركة
                'total_taxes': bill.amount_tax_signed if bill.amount_tax_signed else 0,  # تجميع  او اجمالي قيمة  ضريبة القيمة المضافة
                'bill_amount': bill.amount_untaxed_signed if bill.amount_untaxed_signed else 0,  # قيمة الفاتورة


                'amount_total_signed': bill.amount_total_signed if bill.amount_total_signed else 0,   # الاجمالي
                # صافي الايراد الكلي

                'additional_tax_value': bill.invoice_line_ids.tax_ids[0].name if bill.invoice_line_ids.tax_ids.ids else " ",  # نسبة ضريبة القيمة المضافة

                'date': bill.invoice_date.strftime('%Y-%m-%d') if bill.invoice_date else '',  # تاريخ الفاتورة

                'invoice_num': bill.name or '',  # رقم الفاتورة  =   رقم القيد journal_num
                # 'journal_num': bill.name or '',  # رقم القيد

                'negative_source_tax_value': bill,
                # 'negative_source_tax_value': negative_tax_name,
                # 'negative_source_tax_value': next(
                #     (bill.tax_totals_json for line in bill.invoice_line_ids for tax in line.tax_ids if tax.amount < 0),
                #     ""
                # ),

                'tax_ref_number': bill.partner_id.zip if bill.partner_id.zip else " ",  # رقم التسجيل الضريبي
                'address': bill.partner_id.street if bill.partner_id.street else " ",  # العنوان


            })

        return data



    def action_print_excel_bill_report(self):
        if not self:
            return

        data = self.get_bill_report_data()

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Bill Report')
        worksheet.right_to_left()
        sequence = 0



        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': 'red',
            'font_color': 'white',
            'font_size': 15,
            'border': 1,
        })
        data_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        title_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': 'white',
            'font_size': 16,
            'bg_color': 'red',
            'border': 0,

        })

        collection_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_color': 'white',
            'font_size': 16,
            'bg_color': '#000000',
            'border': 1,
            'border_color': 'white',
        })


       # REPORT TITLE
        worksheet.merge_range(0, 0, 1, 11, ' 2025', title_format)
        worksheet.merge_range(2, 0, 2, 11, ' ', title_format)
        worksheet.merge_range(3, 0, 4, 11, 'تسويات مشتريات ضريبة القيمة المضافة  ', title_format)

        #Header

        worksheet.write(6, 0, '#', header_format)
        worksheet.write(6, 1, 'الشهر', header_format)
        worksheet.write(6, 2, 'المورد', header_format)
        worksheet.write(6, 3, ' نوع الاعمال', header_format)
        worksheet.write(6, 4, 'قيمة الفاتورة', header_format)
        worksheet.write(6, 5, 'ضريبة القيمة المضافة', header_format)
        worksheet.write(6, 6, 'الاجمالي ', header_format)
        worksheet.write(6, 7, 'نسبة الضريبة %', header_format)
        worksheet.write(6, 8, 'تاريخ الفاتورة', header_format)
        worksheet.write(6, 9, 'رقم الفاتورة', header_format)
        worksheet.write(6, 10, 'رقم القيد', header_format)
        worksheet.write(6, 11, 'خصم المنبع', header_format)
        worksheet.write(6, 12, ' رقم التسجيل الضريبي ', header_format)
        worksheet.write(6, 13, 'العنوان ', header_format)


        row = 7
        for line in data:
            sequence+=1
            worksheet.write(row, 0, sequence, data_format)
            worksheet.write(row, 1, line['month'], data_format)
            worksheet.write(row, 2, line['company'], data_format)
            worksheet.write(row, 3, line['industry'], data_format)
            worksheet.write(row, 4, line['total_taxes'], data_format)
            worksheet.write(row, 5, line['bill_amount'], data_format)
            worksheet.write(row, 6, line['amount_total_signed'], data_format)
            worksheet.write(row, 7, line['additional_tax_value'], data_format)
            worksheet.write(row, 8, line['date'], data_format)
            worksheet.write(row, 9, line['invoice_num'], data_format)
            worksheet.write(row, 10, line['invoice_num'], data_format)
            worksheet.write(row, 11, line['negative_source_tax_value'], data_format)
            worksheet.write(row, 12, line['tax_ref_number'], data_format)
            worksheet.write(row, 13, line['address'], data_format)
            row += 1

        workbook.close()
        output.seek(0)

        # Save the generated file to a binary field for the first record
        # You can decide what to do here, I save it to the first record's excel_sheet
        self.excel_sheet = base64.encodebytes(output.read())
        self.bill_report_name = 'Bill Report.xlsx'

        # Return an action to download the file of the first record to avoid singalong error
        return {
            'type': 'ir.actions.act_url',
            'name': 'Bill Excel Report',
            'url': f'/web/content/account.move/{self[0].id}/excel_sheet/{self[0].bill_report_name}?download=true',
            'target': 'self',
        }

