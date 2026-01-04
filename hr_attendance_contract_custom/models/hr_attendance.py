# -*- coding: utf-8 -*-
import pytz
from odoo import models, fields, api
from datetime import datetime, timedelta


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    _description = 'Hr Attendance Custom'

    att_date = fields.Date("Attendance Date")
    over_time = fields.Float("Custom Overtime", readonly=True, compute='_compute_attendances', store=True)
    act_late_in = fields.Float("Late Hours", readonly=True, compute='_compute_attendances', store=True)
    act_diff_time = fields.Float("Diff Hours", readonly=True, compute='_compute_attendances', store=True)
    late_in = fields.Float("Late Penalty")
    diff_time = fields.Float("Diff Penalty")
    is_weekend = fields.Integer("Weekend", readonly=True, compute='_compute_attendances', store=True)
    is_public_holiday = fields.Integer("Public Holiday", readonly=True, compute='_compute_attendances', store=True)
    is_tamper = fields.Integer("Tamper", readonly=True, compute='_compute_attendances', store=True)

    # --- إضافة الدالة الناقصة ---
    def get_attendances(self):
        """ دالة يتم استدعاؤها من الـ Server Action """
        for rec in self:
            rec._compute_attendances()

    @api.depends('check_in', 'check_out', 'employee_id', 'att_date')
    def _compute_attendances(self):
        for rec in self:
            # تمهيد القيم لتجنب الأخطاء
            rec.over_time = 0.0
            rec.act_late_in = 0.0
            rec.act_diff_time = 0.0
            rec.is_weekend = 0
            rec.is_public_holiday = 0
            rec.is_tamper = 0

            if not rec.check_in or not rec.check_out or not rec.employee_id:
                continue

            employee_id = rec.employee_id
            calendar_id = employee_id.resource_calendar_id
            if not calendar_id:
                continue

            calendar_attendance_ids = self.env['resource.calendar.attendance'].search(
                [('calendar_id', '=', calendar_id.id)]
            )

            # --- تصحيح: البحث في hr.contract بدلاً من hr.version ---
            contract_id = self.env['hr.contract'].search([
                ('employee_id', '=', employee_id.id),
                ('state', '=', 'open')
            ], limit=1)

            policy_id = contract_id.att_policy_id if contract_id else False

            # ... (باقي المنطق الحسابي المعقد الخاص بك يظل كما هو) ...
            # ... تأكد فقط من أن الكود الداخلي لا يعتمد على متغيرات غير موجودة ...