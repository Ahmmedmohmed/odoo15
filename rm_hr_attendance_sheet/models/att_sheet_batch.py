# -*- coding: utf-8 -*-

from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
from odoo import models, fields, tools, api, _
from odoo.exceptions import UserError, ValidationError
import babel


class AttendanceSheetBatch(models.Model):
    _name = 'attendance.sheet.batch'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # إضافة خاصية تتبع الرسائل المناسبة لـ V15
    _description = 'Attendance Sheet Batch'

    name = fields.Char("Name", readonly=True, states={'draft': [('readonly', False)]})
    department_id = fields.Many2one('hr.department', 'Department Name',
                                    required=True, readonly=True,
                                    states={'draft': [('readonly', False)]})
    date_from = fields.Date(string='Date From', readonly=True, required=True,
                            states={'draft': [('readonly', False)]},
                            default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_to = fields.Date(string='Date To', readonly=True, required=True,
                          states={'draft': [('readonly', False)]},
                          default=lambda self: fields.Date.to_string(
                              (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))

    att_sheet_ids = fields.One2many(comodel_name='attendance.sheet',
                                    string='Attendance Sheets',
                                    inverse_name='batch_id')
    payslip_batch_id = fields.Many2one(comodel_name='hr.payslip.run',
                                       string='Payslip Batch')

    # في Odoo 15 نستخدم tracking=True بدلاً من track_visibility
    state = fields.Selection([
        ('draft', 'Draft'),
        ('att_gen', 'Attendance Sheets Generated'),
        ('att_sub', 'Attendance Sheets Submitted'),
        ('done', 'Close')], default='draft', string='Status',
        required=True, readonly=True, index=True, tracking=True)

    @api.onchange('department_id', 'date_from', 'date_to')
    def onchange_employee(self):
        if (not self.department_id) or (not self.date_from) or (not self.date_to):
            return
        department = self.department_id
        date_from = self.date_from
        # تحويل التاريخ لـ datetime ليتوافق مع مكتبة babel في V15
        ttyme = datetime.combine(fields.Date.from_string(date_from), time.min)
        locale = self.env.context.get('lang', 'en_US')
        self.name = _('Attendance Batch of %s Department for %s') % (
            department.name,
            tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))

    def action_done(self):
        for batch in self:
            if batch.state != "att_sub":
                continue
            for sheet in batch.att_sheet_ids:
                if sheet.state == 'confirm':
                    sheet.action_approve()  # استدعاء دالة الاعتماد من شيت الحضور
            batch.write({'state': 'done'})

    def action_att_gen(self):
        return self.write({'state': 'att_gen'})

    def gen_att_sheet(self):
        att_sheet_obj = self.env['attendance.sheet']
        for batch in self:
            from_date = batch.date_from
            to_date = batch.date_to
            employee_ids = self.env['hr.employee'].search(
                [('department_id', '=', batch.department_id.id)])

            if not employee_ids:
                raise UserError(_("There is no Employees In This Department"))

            for employee in employee_ids:
                # التأكد من وجود عقد ساري للموظف في Odoo 15
                contract_ids = employee._get_contracts(from_date, to_date)
                if not contract_ids:
                    continue  # أو أظهر تنبيه حسب رغبتك

                new_sheet = att_sheet_obj.create({
                    'employee_id': employee.id,
                    'date_from': from_date,
                    'date_to': to_date,
                    'batch_id': batch.id
                })
                # تشغيل الحسابات التلقائية للحضور
                new_sheet.onchange_employee()
                new_sheet.get_attendances()
            batch.action_att_gen()

    def submit_att_sheet(self):
        for batch in self:
            if batch.state != "att_gen":
                continue
            for sheet in batch.att_sheet_ids:
                if sheet.state == 'draft':
                    sheet.action_confirm()
            batch.write({'state': 'att_sub'})