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

    @api.depends('check_in', 'check_out', 'employee_id', 'att_date')
    def _compute_attendances(self, compute=True):

        employee_ids = self.env['hr.employee'].search([('id', 'in', self.mapped('employee_id.id'))])
        for employee_id in employee_ids:

            calendar_id = employee_id.resource_calendar_id
            if not calendar_id:
                continue

            calendar_attendance_ids = self.env['resource.calendar.attendance'].search(
                [('calendar_id', '=', calendar_id.id)]
            )
            if not calendar_attendance_ids:
                continue

            contract_id = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)])
            policy_id = contract_id[-1].att_policy_id if contract_id else False

            tz = pytz.timezone(employee_id.tz or 'UTC')
            employee_records = self.filtered(lambda x: x.employee_id.id == employee_id.id).sorted(
                key=lambda x: x.check_in or datetime.min
            )

            late_cnt = []
            diff_cnt = []

            for rec in employee_records:
                if not rec.check_in or not rec.check_out:
                    continue

                # تحويل التواريخ إلى aware datetime
                actual_check_in = pytz.utc.localize(rec.check_in).astimezone(tz)
                actual_check_out = pytz.utc.localize(rec.check_out).astimezone(tz)

                att_date = rec.att_date
                if not att_date:
                    # Determine attendance date based on rules
                    min_hour_from = min(calendar_attendance_ids.mapped('hour_from')) if calendar_attendance_ids else 0
                    max_hour_to = max(calendar_attendance_ids.mapped('hour_to')) if calendar_attendance_ids else 24

                    att_date = actual_check_in.date()
                    if min_hour_from < 3 and actual_check_in.hour > 18:
                        att_date += timedelta(days=1)
                    elif calendar_id.is_2days and actual_check_in.hour < 18:
                        att_date -= timedelta(days=1)
                    elif max_hour_to >= 21 and actual_check_in.hour < 9:
                        att_date -= timedelta(days=1)
                    elif max_hour_to < 21 and actual_check_in.hour < 6:
                        att_date -= timedelta(days=1)

                day_num = att_date.weekday()
                check_in_list = []
                check_out_list = []

                # Match calendar attendances
                for cal_att in calendar_attendance_ids:
                    if cal_att.day_period == 'lunch':
                        continue
                    if cal_att.dayofweek != str(day_num):
                        continue

                    if cal_att.hour_from is not None:
                        hour_from_dt = datetime(att_date.year, att_date.month, att_date.day,
                                                int(cal_att.hour_from),
                                                int((cal_att.hour_from % 1) * 60))
                        hour_from_dt = tz.localize(hour_from_dt)
                    else:
                        hour_from_dt = None

                    if cal_att.hour_to is not None:
                        hour_to_dt = datetime(att_date.year, att_date.month, att_date.day,
                                              int(cal_att.hour_to),
                                              int((cal_att.hour_to % 1) * 60))
                        hour_to_dt = tz.localize(hour_to_dt)
                    else:
                        hour_to_dt = None

                    if hour_from_dt and hour_to_dt:
                        if hour_from_dt <= actual_check_in <= hour_to_dt:
                            check_in_list.append(cal_att.hour_from)
                            check_out_list.append(cal_att.hour_to)
                    elif hour_from_dt:
                        if actual_check_in >= hour_from_dt:
                            check_in_list.append(cal_att.hour_from)
                            check_out_list.append(cal_att.hour_to)
                    else:
                        check_in_list.append(cal_att.hour_from)
                        check_out_list.append(cal_att.hour_to)

                # Determine planned check-in/out times
                planned_check_in, planned_check_out = None, None
                if check_in_list:
                    in_hour = min(check_in_list)
                    in_minutes = int((in_hour % 1) * 60)
                    planned_check_in = datetime(att_date.year, att_date.month, att_date.day,
                                                int(in_hour), in_minutes)
                    planned_check_in = tz.localize(planned_check_in)
                if check_out_list:
                    out_hour = max(check_out_list)
                    out_minutes = int((out_hour % 1) * 60)
                    planned_check_out = datetime(att_date.year, att_date.month, att_date.day,
                                                 int(out_hour), out_minutes)
                    planned_check_out = tz.localize(planned_check_out)

                # Calculate late, diff, overtime
                late_in = max((actual_check_in - planned_check_in).total_seconds() / 3600, 0) if planned_check_in else 0
                diff_time = max((planned_check_out - actual_check_out).total_seconds() / 3600, 0) if planned_check_out else 0
                over_time = max((actual_check_out - planned_check_out).total_seconds() / 3600, 0) if planned_check_out else rec.worked_hours

                # Weekend
                is_weekend = 1 if planned_check_in is None else 0

                # Public holiday
                public_holidays = self.env['resource.calendar.leaves'].search([
                    ('company_id', '=', rec.employee_id.company_id.id),
                    '|', ('calendar_id', '=', calendar_id.id), ('calendar_id', '=', False)
                ])
                is_public_holiday = 0
                for ph in public_holidays:
                    if ph.date_from.date() <= att_date <= ph.date_to.date():
                        is_public_holiday = 1
                        over_time = rec.worked_hours
                        late_in = 0
                        diff_time = 0
                        break

                # Tamper check
                is_tamper = 1 if (actual_check_out - actual_check_in).total_seconds() / 3600 < 2 else 0

                values = {
                    'over_time': over_time,
                    'act_late_in': late_in,
                    'act_diff_time': diff_time,
                    'is_weekend': is_weekend,
                    'is_public_holiday': is_public_holiday,
                    'is_tamper': is_tamper,
                }

                rec.write(values)
                rec.att_date = att_date
