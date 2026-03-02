# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import babel
from datetime import datetime, timedelta


class HrAttendancePolicy(models.Model):
    _name = 'hr.attendance.policy'
    _description = 'Attendance Sheet Policies'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # إضافة خاصية التتبع والدردشة لضمان استقرار V15

    name = fields.Char(string="Name", required=True, tracking=True)
    overtime_rule_ids = fields.Many2many(
        comodel_name="hr.overtime.rule",
        relation="overtime_rule_policy_rel",
        column1="attendance_policy_col",
        column2="overtime_rule_col",
        string="Overtime Rules")

    late_rule_id = fields.Many2one(
        comodel_name="hr.late.rule",
        required=True,
        string="Late In Rule",
        tracking=True)

    absence_rule_id = fields.Many2one(
        comodel_name="hr.absence.rule",
        string="Absence Rule",
        required=True,
        tracking=True)

    diff_rule_id = fields.Many2one(
        comodel_name="hr.diff.rule",
        string="Difference Time Rule",
        required=True,
        tracking=True)

    # الدوال (get_overtime, get_late, get_diff, get_absence) سليمة تماماً ولا تحتاج لتغيير
    def get_overtime(self):
        self.ensure_one()
        res = {}
        if self:
            overtime_ids = self.overtime_rule_ids
            wd_ot_id = self.overtime_rule_ids.search(
                [('type', '=', 'workday'), ('id', 'in', overtime_ids.ids)],
                order='id', limit=1)
            we_ot_id = self.overtime_rule_ids.search(
                [('type', '=', 'weekend'), ('id', 'in', overtime_ids.ids)],
                order='id', limit=1)
            ph_ot_id = self.overtime_rule_ids.search(
                [('type', '=', 'ph'), ('id', 'in', overtime_ids.ids)],
                order='id', limit=1)

            res['wd_rate'] = wd_ot_id.rate if wd_ot_id else 0
            res['wd_after'] = wd_ot_id.active_after if wd_ot_id else 0
            res['we_rate'] = we_ot_id.rate if we_ot_id else 0
            res['we_after'] = we_ot_id.active_after if we_ot_id else 0
            res['ph_rate'] = ph_ot_id.rate if ph_ot_id else 0
            res['ph_after'] = ph_ot_id.active_after if ph_ot_id else 0
        return res

    # بقية الدوال (get_late, get_diff, get_absence) تظل كما هي في كودك الأصلي
    # ... (تكملة الكود الأصلي) ...


class HrOvertimeRule(models.Model):
    _name = 'hr.overtime.rule'
    _description = 'Over time Rules'

    # تحويل قائمة الـ Selection لمتغير ثابت لسهولة الصيانة في V15
    OT_TYPES = [
        ('weekend', 'Week End'),
        ('workday', 'Working Day'),
        ('ph', 'Public Holiday')
    ]

    name = fields.Char(string="Name", required=True)
    type = fields.Selection(selection=OT_TYPES, string="Type", default='workday', required=True)
    active_after = fields.Float(string="Apply after (Hours)", help="After this time the overtime will be calculated")
    rate = fields.Float(string='Rate', default=1.0)

# استكمال بقية الكلاسات (HrLateRule, HrDiffRule, HrAbsenceRule) بنفس منطق كودك الأصلي