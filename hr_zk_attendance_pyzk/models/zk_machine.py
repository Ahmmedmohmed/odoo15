# -*- coding: utf-8 -*-

import pytz
from datetime import datetime, timedelta
import logging
from odoo import fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

try:
    from zk import ZK, const
except ImportError:
    _logger.error("Unable to import pyzk library. Try 'pip3 install pyzk'.")


class ZkMachine(models.Model):
    _name = 'zk.machine'
    _description = 'ZK Biometric Device'

    name = fields.Char(string='Machine IP', required=True)
    port_no = fields.Integer(string='Port No', required=True, default=4370)
    address_id = fields.Many2one('res.partner', string='Working Address')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    # الحقول التي كانت ناقصة
    zk_timeout = fields.Integer(string='ZK Timeout', required=True, default=120)
    zk_after_date = fields.Datetime(string='Attend Start Date',
                                    help='If provided, Attendance module will ignore records before this date.')

    def device_connect(self, zkobj):
        try:
            conn = zkobj.connect()
            return conn
        except Exception as e:
            _logger.info(f"zk.exception.ZKNetworkError: {e}")
            return False

    def try_connection(self):
        for info in self:
            machine_ip = info.name
            zk_port = info.port_no
            timeout = info.zk_timeout
            try:
                zk = ZK(machine_ip, port=zk_port, timeout=timeout, password=0, force_udp=False, ommit_ping=True)
            except NameError:
                raise UserError(_("Pyzk module not Found. Please install it with 'pip3 install pyzk'."))

            conn = self.device_connect(zk)
            if conn:
                conn.disconnect()
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'success',
                        'title': _("Connection Test"),
                        'message': 'Biometric Device is Up/Reachable.',
                        'next': {'type': 'ir.actions.act_window_close'},
                    }
                }
            else:
                raise UserError(_("Biometric Device is Down/Unreachable."))

    def clear_attendance(self):
        for info in self:
            try:
                machine_ip = info.name
                zk_port = info.port_no
                timeout = info.zk_timeout
                try:
                    zk = ZK(machine_ip, port=zk_port, timeout=timeout, password=0, force_udp=False, ommit_ping=False)
                except NameError:
                    raise UserError(_("Pyzk module not Found. Please install it with 'pip3 install pyzk'."))

                conn = self.device_connect(zk)
                if conn:
                    conn.enable_device()
                    clear_data = zk.get_attendance()
                    if clear_data:
                        # تحذير: هذا يمسح البيانات من أودو فقط (الجدول الوسيط)
                        self.env.cr.execute("""DELETE FROM zk_machine_attendance""")
                        conn.disconnect()
                        return {
                            'type': 'ir.actions.client',
                            'tag': 'display_notification',
                            'params': {
                                'type': 'warning',
                                'title': _("Clear Logs"),
                                'message': _('Attendance Records Deleted from Odoo buffer.'),
                            }
                        }
                    else:
                        raise UserError(_('Unable to clear Attendance log. Are you sure attendance log is not empty.'))
                else:
                    raise UserError(_('Unable to connect to Attendance Device.'))
            except Exception as e:
                raise ValidationError(f'Error: {str(e)}')

    def cron_download(self):
        machines = self.env['zk.machine'].search([])
        for machine in machines:
            machine.download_attendance()

    def download_attendance(self):
        _logger.info("++++++++++++ Cron Executed: Download Attendance ++++++++++++++++++++++")
        zk_attendance = self.env['zk.machine.attendance']
        for info in self:
            machine_ip = info.name
            zk_port = info.port_no
            timeout = info.zk_timeout
            try:
                zk = ZK(machine_ip, port=zk_port, timeout=timeout, password=0, force_udp=False, ommit_ping=True)
            except NameError:
                raise UserError(_("Pyzk module not Found. Please install it with 'pip3 install pyzk'."))

            conn = self.device_connect(zk)
            if conn:
                try:
                    attendance = conn.get_attendance()
                except:
                    attendance = False

                if attendance:
                    for each in attendance:
                        atten_time = each.timestamp
                        if isinstance(atten_time, str):
                            atten_time = datetime.strptime(atten_time, '%Y-%m-%d %H:%M:%S')

                        if not info.zk_after_date:
                            tmp_zk_after_date = datetime.strptime('2020-01-01', "%Y-%m-%d")
                        else:
                            tmp_zk_after_date = info.zk_after_date

                        if atten_time and atten_time > tmp_zk_after_date:
                            local_tz = pytz.timezone(self.env.user.partner_id.tz or 'UTC')
                            local_dt = local_tz.localize(atten_time, is_dst=None)
                            utc_dt = local_dt.astimezone(pytz.utc)
                            final_atten_time = utc_dt.replace(tzinfo=None)

                            # البحث عن الموظف
                            employee = self.env['hr.employee'].sudo().search(
                                [('device_id', '=', each.user_id)], limit=1)

                            if employee:
                                duplicate = zk_attendance.sudo().search([
                                    ('device_id', '=', each.user_id),
                                    ('punching_time', '=', final_atten_time)
                                ], limit=1)

                                if not duplicate:
                                    zk_attendance.create({
                                        'employee_id': employee.id,
                                        'punching_time': final_atten_time,
                                        'device_id': each.user_id,
                                        'address_id': info.address_id.id,
                                        'is_sent': False
                                    })

                conn.disconnect()
                self._calculate_check_in_out()
                return True
            else:
                _logger.warning("Could not connect to device.")

    def _get_all_dates(self, start_date, end_date):
        all_dates = []
        for n in range((end_date - start_date).days + 1):
            date_to_add = start_date + timedelta(days=n)
            all_dates.append(date_to_add)
        return all_dates

    def _calculate_check_in_out(self):
        # البحث عن البيانات غير المعالجة
        if not self.env.context.get('recalc'):
            zk_att_obj = self.env['zk.machine.attendance'].sudo().search([('is_sent', '!=', True)])
        else:
            zk_att_obj = self.env['zk.machine.attendance'].sudo().search([('is_sent', '=', True)])

        if zk_att_obj:
            att_obj = self.env['hr.attendance']
            employee_ids = zk_att_obj.mapped('employee_id')

            # تحديد تواريخ العمل
            dates = zk_att_obj.mapped('punching_time')
            if not dates: return

            start_date = min(dates).date() - timedelta(days=1)
            end_date = max(dates).date()
            get_dates = self._get_all_dates(start_date, end_date)

            for employee in employee_ids:
                if not employee.resource_calendar_id: continue

                calendar_lines = employee.resource_calendar_id.attendance_ids
                tz = pytz.timezone(employee.tz or 'UTC')

                for d in get_dates:
                    check_in_list = []
                    check_out_list = []
                    day_num = d.weekday()

                    for line in calendar_lines:
                        if line.day_period == 'lunch': continue

                        is_today = False
                        if line.dayofweek == str(day_num):
                            is_today = True

                        if is_today:
                            check_in_list.append(line.hour_from)
                            check_out_list.append(line.hour_to)

                    if not check_in_list: continue

                    # منطق الورديات
                    is_2days = getattr(employee.resource_calendar_id, 'is_2days', False)
                    if is_2days:
                        next_d = d + timedelta(days=1)
                        planned_in = datetime.combine(d, datetime.min.time()) + timedelta(hours=min(check_in_list))
                        planned_out = datetime.combine(next_d, datetime.min.time()) + timedelta(
                            hours=max(check_out_list))
                    else:
                        planned_in = datetime.combine(d, datetime.min.time()) + timedelta(hours=min(check_in_list))
                        planned_out = datetime.combine(d, datetime.min.time()) + timedelta(hours=max(check_out_list))

                    local_dt_in = tz.localize(planned_in, is_dst=None)
                    local_dt_out = tz.localize(planned_out, is_dst=None)
                    planned_check_in = local_dt_in.astimezone(pytz.utc).replace(tzinfo=None)
                    planned_check_out = local_dt_out.astimezone(pytz.utc).replace(tzinfo=None)

                    in_list = []
                    out_list = []

                    for rec in zk_att_obj:
                        if rec.employee_id == employee:
                            diff_in = (rec.punching_time - planned_check_in).total_seconds() / 3600
                            diff_out = (rec.punching_time - planned_check_out).total_seconds() / 3600

                            if -3.0 <= diff_in <= 3.0:
                                in_list.append(rec.punching_time)
                                rec.is_sent = True
                            elif -3.0 <= diff_out <= 9.0:
                                out_list.append(rec.punching_time)
                                rec.is_sent = True

                    check_in = min(in_list) if in_list else False
                    check_out = max(out_list) if out_list else False

                    # إنشاء الحضور
                    if check_in:
                        # البحث عن سجلات موجودة لتجنب التكرار
                        search_domain = [('employee_id', '=', employee.id),
                                         ('check_in', '>=', planned_check_in - timedelta(hours=4)),
                                         ('check_in', '<=', planned_check_in + timedelta(hours=18))]
                        existing = att_obj.search(search_domain, limit=1)

                        if existing:
                            if check_in < existing.check_in:
                                existing.write({'check_in': check_in})
                            if check_out:
                                if not existing.check_out or check_out > existing.check_out:
                                    existing.write({'check_out': check_out})
                        else:
                            att_obj.create({
                                'employee_id': employee.id,
                                'check_in': check_in,
                                'check_out': check_out if (check_out and check_out > check_in) else False
                            })

            # تعليم السجلات كمرسلة
            if not self.env.context.get('recalc'):
                for rec in zk_att_obj:
                    rec.is_sent = True