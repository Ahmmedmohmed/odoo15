# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # علاقة ربط شيتات الحضور بقسيمة الراتب
    attendance_sheet_ids = fields.One2many(
        comodel_name='attendance.sheet',
        inverse_name='payslip_id',
        string='Attendance Sheets'
    )

    # حقول التجميع (Computed Fields) لضمان ظهور البيانات في واجهة الـ Payslip
    overtime_no = fields.Integer(string="Overtime No", compute='_compute_att_sheet_data', store=True)
    overtime_hours = fields.Float(string="Overtime Hours", compute='_compute_att_sheet_data', store=True)
    late_no = fields.Integer(string="Late No", compute='_compute_att_sheet_data', store=True)
    late_hours = fields.Float(string="Late Hours", compute='_compute_att_sheet_data', store=True)
    absent_no = fields.Integer(string="Absent No", compute='_compute_att_sheet_data', store=True)
    absent_hours = fields.Float(string="Absent Hours", compute='_compute_att_sheet_data', store=True)
    diff_no = fields.Integer(string="Diff No", compute='_compute_att_sheet_data', store=True)
    diff_hours = fields.Float(string="Diff Hours", compute='_compute_att_sheet_data', store=True)
    worked_days = fields.Integer(string="Work Days No", compute='_compute_att_sheet_data', store=True)
    worked_hours = fields.Float(string="Work Days Hours", compute='_compute_att_sheet_data', store=True)

    @api.depends('attendance_sheet_ids', 'attendance_sheet_ids.state')
    def _compute_att_sheet_data(self):
        """ تجميع بيانات الحضور من الشيتات المعتمدة فقط لنسخة 15 """
        for slip in self:
            res = {
                'overtime_no': 0, 'overtime_hours': 0,
                'late_no': 0, 'late_hours': 0,
                'absent_no': 0, 'absent_hours': 0,
                'diff_no': 0, 'diff_hours': 0,
                'worked_hours': 0
            }
            for sheet in slip.attendance_sheet_ids.filtered(lambda s: s.state == 'done'):
                res['overtime_no'] += sheet.no_overtime
                res['overtime_hours'] += sheet.tot_overtime
                res['late_no'] += sheet.no_late
                res['late_hours'] += sheet.tot_late
                res['absent_no'] += sheet.no_absence
                res['absent_hours'] += sheet.tot_absence
                res['diff_no'] += sheet.no_difftime
                res['diff_hours'] += sheet.tot_difftime
                res['worked_hours'] += sheet.tot_worked_hour

            slip.update(res)

    def set_payslip_attendance_sheet(self):
        """ البحث عن شيتات الحضور المعتمدة للفترة المحددة في أودو 15 """
        self.ensure_one()
        sheet_ids = self.env['attendance.sheet'].search([
            ('employee_id', '=', self.employee_id.id),
            ('date_from', '>=', self.date_from),
            ('date_to', '<=', self.date_to),
            ('state', '=', 'done')
        ])
        if sheet_ids:
            # استخدام Command (6, 0, ids) لضمان الربط الصحيح في V15
            self.attendance_sheet_ids = [(6, 0, sheet_ids.ids)]

    def _get_new_worked_days_lines(self):
        """
        تعديل جوهري لـ Odoo 15:
        إجبار قسيمة الراتب على سحب البيانات من شيت الحضور عند الضغط على Compute Sheet
        """
        if self.contract_id and self.contract_id.attendance_sheet_based:
            self.set_payslip_attendance_sheet()
        return super(HrPayslip, self)._get_new_worked_days_lines()

    def compute_sheet(self):
        """
        التحقق من وجود شيت حضور معتمد قبل الحساب في نسخة 15
        لأن الرواتب تعتمد كلياً على منطق الـ Attendance Sheet هنا
        """
        for slip in self:
            if slip.contract_id and slip.contract_id.attendance_sheet_based:
                slip.set_payslip_attendance_sheet()
                if not slip.attendance_sheet_ids:
                    raise UserError(_('No Approved Attendance Sheet Found For Employee: %s') % (slip.employee_id.name))
        return super(HrPayslip, self).compute_sheet()