# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AttendanceSheetLineChange(models.TransientModel):
    _name = "attendance.sheet.line.change"
    _description = "Change Attendance Line Data Wizard"

    overtime = fields.Float("Overtime")
    late_in = fields.Float("Late In")
    diff_time = fields.Float("Diff Time")
    note = fields.Text("Note", required=True)
    att_line_id = fields.Many2one(comodel_name="attendance.sheet.line")

    @api.model
    def default_get(self, fields_list):
        """ جلب البيانات الافتراضية من السطر المختار في Odoo 15 """
        res = super(AttendanceSheetLineChange, self).default_get(fields_list)
        # التأكد من وجود active_id في السياق لضمان عدم حدوث خطأ
        active_id = self._context.get('active_id')
        if active_id and self._context.get('active_model') == 'attendance.sheet.line':
            line = self.env['attendance.sheet.line'].browse(active_id)
            res.update({
                'overtime': line.overtime,
                'late_in': line.late_in,
                'diff_time': line.diff_time,
                'att_line_id': line.id,
            })
        return res

    def change_att_data(self):
        """ تحديث بيانات سطر الحضور وإغلاق النافذة المنبثقة لنسخة 15 """
        self.ensure_one()
        # الوصول المباشر للحقول أكثر أماناً في Odoo 15 من استخدام read()
        if self.att_line_id:
            self.att_line_id.write({
                'overtime': self.overtime,
                'late_in': self.late_in,
                'diff_time': self.diff_time,
                'note': self.note,
            })
            # بعد التحديث، من المهم إعادة حساب إجماليات الشيت في V15
            if self.att_line_id.att_sheet_id:
                self.att_line_id.att_sheet_id._compute_sheet_total()

        return {'type': 'ir.actions.act_window_close'}