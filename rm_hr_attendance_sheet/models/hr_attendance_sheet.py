# -*- coding: utf-8 -*-

import pytz
from datetime import datetime, date, timedelta, time
from dateutil.relativedelta import relativedelta
from odoo import models, fields, tools, api, exceptions, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import format_date

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"
import logging

_logger = logging.getLogger(__name__)


class AttendanceSheet(models.Model):
    _name = 'attendance.sheet'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # في 15 نستخدم mail.thread بدلاً من mail.thread.cc
    _description = 'Hr Attendance Sheet'

    name = fields.Char("Name", tracking=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee', required=True)
    batch_id = fields.Many2one(comodel_name='attendance.sheet.batch', string='Attendance Sheet Batch')
    department_id = fields.Many2one(related='employee_id.department_id', string='Department', store=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.company,
                                 states={'draft': [('readonly', False)]})
    date_from = fields.Date(string='Date From', readonly=True, required=True,
                            states={'draft': [('readonly', False)]},
                            default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_to = fields.Date(string='Date To', readonly=True, required=True,
                          states={'draft': [('readonly', False)]},
                          default=lambda self: fields.Date.to_string(
                              (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))

    line_ids = fields.One2many(comodel_name='attendance.sheet.line', string='Attendances',
                               readonly=True, inverse_name='att_sheet_id')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Approved')], default='draft', string='Status', required=True, readonly=True, index=True,
        tracking=True)

    # الحقول المحسوبة (Calculated Fields) - في 15 يفضل بقاؤها store=True لسرعة التقارير
    no_overtime = fields.Integer(compute="_compute_sheet_total", string="No of overtimes", readonly=True, store=True)
    tot_overtime = fields.Float(compute="_compute_sheet_total", string="Total Over Time", readonly=True, store=True)
    tot_difftime = fields.Float(compute="_compute_sheet_total", string="Total Diff time Hours", readonly=True,
                                store=True)
    no_difftime = fields.Integer(compute="_compute_sheet_total", string="No of Diff Times", readonly=True, store=True)
    tot_late = fields.Float(compute="_compute_sheet_total", string="Total Late In", readonly=True, store=True)
    no_late = fields.Integer(compute="_compute_sheet_total", string="No of Lates", readonly=True, store=True)
    no_absence = fields.Integer(compute="_compute_sheet_total", string="No of Absence Days", readonly=True, store=True)
    tot_absence = fields.Float(compute="_compute_sheet_total", string="Total absence Hours", readonly=True, store=True)
    tot_worked_hour = fields.Float(compute="_compute_sheet_total", string="Total Worked Hours", readonly=True,
                                   store=True)

    att_policy_id = fields.Many2one(comodel_name='hr.attendance.policy', string="Attendance Policy", required=True)
    payslip_id = fields.Many2one(comodel_name='hr.payslip', string='PaySlip')
    contract_id = fields.Many2one('hr.contract', string='Contract', readonly=True,
                                  states={'draft': [('readonly', False)]})

    # ... (دوال unlink و check_date تظل كما هي) ...

    def action_approve(self):
        # في Odoo 15، عملية الربط مع Payslip تتطلب دقة في استدعاء الـ Worked Days
        self.action_create_payslip()
        self.write({'state': 'done'})

    def action_create_payslip(self):
        payslip_obj = self.env['hr.payslip']
        payslips = payslip_obj
        for sheet in self:
            contracts = sheet.employee_id._get_contracts(sheet.date_from, sheet.date_to)
            if not contracts:
                raise ValidationError(_('There is no active contract for current employee'))
            if sheet.payslip_id:
                raise ValidationError(_('Payslip Has Been Created Before'))

            # منطق تسمية شيت الراتب في نسخة 15
            struct = contracts[0].structure_type_id.default_struct_id
            name = '%s - %s - %s' % (struct.payslip_name or 'Salary Slip', sheet.employee_id.name,
                                     format_date(self.env, sheet.date_from, date_format="MMMM y"))

            payslip_id = payslip_obj.create({
                'name': name,
                'employee_id': sheet.employee_id.id,
                'date_from': sheet.date_from,
                'date_to': sheet.date_to,
                'contract_id': contracts[0].id,
                'struct_id': struct.id,
            })

            # تعديل Worked Days في Odoo 15 لربط ساعات الغياب والتأخير
            worked_day_lines = self._get_workday_lines()
            payslip_id.worked_days_line_ids = [(0, 0, x) for x in worked_day_lines]

            # تشغيل الحسابات في نسخة 15
            payslip_id.compute_sheet()
            sheet.payslip_id = payslip_id
            payslips += payslip_id
        return payslips

    def _get_workday_lines(self):
        self.ensure_one()
        # في Odoo 15، البحث عن أنواع مدخلات العمل يعتمد على الكود مباشرة
        work_entry_obj = self.env['hr.work.entry.type']

        # مصفوفة البيانات المطلوبة لـ Worked Days في Odoo 15
        res = []
        mapping = [
            ('OVT', 'ATTSHOT', self.no_overtime, self.tot_overtime, 30),
            ('ABS', 'ATTSHAB', self.no_absence, self.tot_absence, 35),
            ('LATE', 'ATTSHLI', self.no_late, self.tot_late, 40),
            ('DIFFT', 'ATTSHDT', self.no_difftime, self.tot_difftime, 45),
        ]

        for code, entry_code, number_of_days, number_of_hours, sequence in mapping:
            work_entry_type = work_entry_obj.search([('code', '=', entry_code)], limit=1)
            if not work_entry_type:
                raise ValidationError(_('Please Add Work Entry Type With Code %s') % entry_code)

            res.append({
                'name': work_entry_type.name,
                'code': code,
                'work_entry_type_id': work_entry_type.id,
                'sequence': sequence,
                'number_of_days': number_of_days,
                'number_of_hours': number_of_hours,
            })
        return res

    # ... (بقية دوال get_attendances و get_attendance_intervals تظل كما هي لأن منطقها سليم لـ 15) ...


class AttendanceSheetLine(models.Model):
    _name = 'attendance.sheet.line'
    _description = 'Attendance Sheet Line'

    state = fields.Selection(related='att_sheet_id.state', store=True)
    date = fields.Date("Date")
    day = fields.Selection([
        ('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'),
        ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')
    ], 'Day of Week', required=True, index=True)
    att_sheet_id = fields.Many2one(comodel_name='attendance.sheet', ondelete="cascade", string='Attendance Sheet',
                                   readonly=True)
    employee_id = fields.Many2one(related='att_sheet_id.employee_id', string='Employee',
                                  store=True)  # إضافة store=True للبحث في V15

    # حقول البيانات الأساسية
    pl_sign_in = fields.Float("Planned sign in", readonly=True)
    pl_sign_out = fields.Float("Planned sign out", readonly=True)
    ac_sign_in = fields.Float("Actual sign in", readonly=True)
    ac_sign_out = fields.Float("Actual sign out", readonly=True)
    worked_hours = fields.Float("Worked Hours", readonly=True)
    overtime = fields.Float("Overtime", readonly=True)
    act_overtime = fields.Float("Actual Overtime", readonly=True)
    late_in = fields.Float("Late In", readonly=True)
    act_late_in = fields.Float("Actual Late In", readonly=True)
    diff_time = fields.Float("Diff Time", readonly=True)
    act_diff_time = fields.Float("Actual Diff Time", readonly=True)

    status = fields.Selection([
        ('ab', 'Absence'), ('weekend', 'Week End'),
        ('ph', 'Public Holiday'), ('leave', 'Leave')
    ], string="Status", readonly=True)
    note = fields.Text("Note", readonly=True)