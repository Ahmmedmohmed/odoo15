# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrContract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    # إضافة خاصية التتبع (tracking=True) لضمان ظهور التغييرات في الـ Chatter لنسخة 15
    att_policy_id = fields.Many2one(
        'hr.attendance.policy',
        string='Attendance Policy',
        tracking=True,
        help="Select the attendance policy for this employee."
    )

    auto_attendance_sheet = fields.Boolean(
        'Auto Generate Attendance Sheet',
        default=False,
        tracking=True,
        help="If checked, the system will automatically create attendance sheets for this contract via cron."
    )

    attendance_sheet_based = fields.Boolean(
        'Based ON Attendance Sheet',
        default=False,
        tracking=True,
        help="If checked, the payslip will fetch worked days data directly from the approved attendance sheet."
    )