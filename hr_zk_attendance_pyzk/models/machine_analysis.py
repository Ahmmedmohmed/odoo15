# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    device_id = fields.Char(string='Biometric Device ID')

    @api.constrains('device_id')
    def check_unique_deviceid(self):
        for employee in self:
            if employee.device_id:
                records = self.env['hr.employee'].search([
                    ('device_id', '=', employee.device_id),
                    ('id', '!=', employee.id)
                ])
                if records:
                    raise ValidationError(_('Another Employee with same Biometric Device ID (%s) already exists.') % employee.device_id)


class ZkMachineAttendance(models.Model):
    _name = 'zk.machine.attendance'
    _description = 'Zk Attendance Log'
    _order = 'punching_time desc'

    device_id = fields.Char(string='Biometric Device ID')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    punching_time = fields.Datetime(string='Punching Time', required=True)
    address_id = fields.Many2one('res.partner', string='Working Address')
    is_sent = fields.Boolean('Is Processed?', default=False, help="If True, this record has been used to create HR Attendance.")


class ReportZkDevice(models.Model):
    _name = 'zk.report.daily.attendance'
    _description = 'ZK Daily Attendance Report'
    _auto = False
    _order = 'punching_day desc'

    name = fields.Many2one('hr.employee', string='Employee')
    punching_day = fields.Date(string='Date')
    address_id = fields.Many2one('res.partner', string='Working Address')
    punching_time = fields.Datetime(string='Punching Time')
    is_sent = fields.Boolean('Is Processed?')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'zk_report_daily_attendance')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW zk_report_daily_attendance AS (
                SELECT
                    min(z.id) as id,
                    z.employee_id as name,
                    z.punching_time::date as punching_day,
                    z.address_id as address_id,
                    z.punching_time as punching_time,
                    z.is_sent as is_sent
                FROM zk_machine_attendance z
                JOIN hr_employee e ON (z.employee_id = e.id)
                GROUP BY
                    z.employee_id,
                    z.punching_time::date,
                    z.address_id,
                    z.punching_time,
                    z.is_sent
            )
        """)