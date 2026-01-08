# -*- coding: utf-8 -*-

import pytz
import logging
from datetime import datetime, timedelta
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

# محاولة استيراد المكتبة سواء كانت مسطبة pip أو موجودة كملفات
try:
    from zk import ZK, const
except ImportError:
    try:
        from . import zklib
        from .zkconst import *
    except ImportError:
        _logger.error("Unable to import pyzk library. Try 'pip3 install pyzk'.")


class ZkMachine(models.Model):
    _name = 'zk.machine'
    _description = 'ZK Biometric Device'

    name = fields.Char(string='Machine IP', required=True, help="IP Address, e.g. 192.168.1.201")
    port_no = fields.Integer(string='Port No', required=True, default=4370)
    address_id = fields.Many2one('res.partner', string='Working Address')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

    # --- الحقول الجديدة (ميزات 19) ---
    zk_timeout = fields.Integer(string='ZK Timeout', required=True, default=10)
    zk_after_date = fields.Date(string='Attend Start Date', help='Ignore records before this date.')

    def device_connect(self, zkobj):
        try:
            conn = zkobj.connect()
            return conn
        except Exception as e:
            return False

    def try_connection(self):
        """ دالة زر اختبار الاتصال """
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
                        'sticky': False,
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
                    raise UserError(_("Pyzk module not Found."))

                conn = self.device_connect(zk)
                if conn:
                    conn.enable_device()
                    clear_data = zk.get_attendance()
                    if clear_data:
                        # تنظيف الجدول الوسيط في أودو
                        self.env.cr.execute("""DELETE FROM zk_machine_attendance WHERE address_id = %s""",
                                            (info.address_id.id,))
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
                        raise UserError(_('Log is already empty.'))
                else:
                    raise UserError(_('Unable to connect to Device.'))
            except Exception as e:
                raise ValidationError(f'Error: {str(e)}')

    def cron_download(self):
        machines = self.env['zk.machine'].search([])
        for machine in machines:
            machine.download_attendance()

    def download_attendance(self):
        _logger.info("++++++++++++ Download Attendance Started ++++++++++++++++++++++")
        zk_attendance = self.env['zk.machine.attendance']

        for info in self:
            machine_ip = info.name
            zk_port = info.port_no
            timeout = info.zk_timeout

            try:
                zk = ZK(machine_ip, port=zk_port, timeout=timeout, password=0, force_udp=False, ommit_ping=True)
            except NameError:
                raise UserError(_("Pyzk module not Found."))

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

                        # فلترة التاريخ
                        if not info.zk_after_date:
                            tmp_zk_after_date = datetime.strptime('2020-01-01', "%Y-%m-%d").date()
                        else:
                            tmp_zk_after_date = info.zk_after_date

                        if atten_time.date() >= tmp_zk_after_date:
                            local_tz = pytz.timezone(self.env.user.partner_id.tz or 'UTC')
                            local_dt = local_tz.localize(atten_time, is_dst=None)
                            utc_dt = local_dt.astimezone(pytz.utc)
                            final_atten_time = utc_dt.replace(tzinfo=None)

                            # البحث عن الموظف بالـ Device ID
                            employee = self.env['hr.employee'].sudo().search(
                                [('device_id', '=', each.user_id)], limit=1)

                            if employee:
                                duplicate = zk_attendance.sudo().search([
                                    ('employee_id', '=', employee.id),
                                    ('punching_time', '=', final_atten_time)
                                ], limit=1)

                                if not duplicate:
                                    zk_attendance.create({
                                        'employee_id': employee.id,
                                        'punching_time': final_atten_time,
                                        'device_id': each.user_id,
                                        'address_id': info.address_id.id,
                                        'punch_type': str(each.punch),
                                        'attendance_type': str(each.status)
                                    })

                conn.disconnect()
                # تشغيل الحساب الذكي (الورديات)
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
        # البحث عن السجلات غير المعالجة (التي لم يتم نقلها لـ HR Attendance)
        # ملاحظة: سنعتمد على أن السجلات التي تم إنشاؤها للتو ليس لها مثيل في hr.attendance
        # أو يمكنك إضافة حقل is_sent كما في الكود السابق، ولكن لتبسيط الدمج مع كودك الحالي:

        # سنجلب كل البصمات من الجدول الوسيط ونعالجها
        # لتحسين الأداء، يفضل إضافة حقل is_sent في الموديل zk.machine.attendance
        # لكن سأكتب كوداً يعمل على الهيكل الحالي لديك

        zk_att_records = self.env['zk.machine.attendance'].search([], order='punching_time asc')
        if not zk_att_records: return

        att_obj = self.env['hr.attendance']

        for record in zk_att_records:
            # تحقق بسيط: هل هذه البصمة مسجلة بالفعل كـ Check In أو Check Out؟
            # هذا المنطق يعتمد على الترتيب الزمني (First In, Last Out Logic)

            # البحث عن آخر حضور مفتوح (بدون انصراف) لهذا الموظف
            last_attendance = att_obj.search([
                ('employee_id', '=', record.employee_id.id),
                ('check_out', '=', False)
            ], limit=1, order='check_in desc')

            if not last_attendance:
                # لا يوجد حضور مفتوح -> إنشاء حضور جديد (Check In)
                att_obj.create({
                    'employee_id': record.employee_id.id,
                    'check_in': record.punching_time
                })
            else:
                # يوجد حضور مفتوح
                # هل البصمة الجديدة في نفس اليوم؟ وهل هي متأخرة عن الدخول؟
                # وهل الفرق بينها وبين الدخول معقول (مثلاً أكثر من دقيقة) لتجنب التكرار؟

                time_diff = (record.punching_time - last_attendance.check_in).total_seconds()

                if time_diff > 60:  # فرق دقيقة
                    # نعتبرها انصراف (Check Out) وتحديث السجل
                    last_attendance.write({'check_out': record.punching_time})

                # ملاحظة: إذا كان هناك بصمة ثالثة في نفس اليوم، الكود أعلاه سيقوم بإنشاء Check In جديد
                # وهذا هو السلوك الافتراضي لأودو.

        # تنظيف الجدول الوسيط بعد المعالجة (اختياري، لكن يفضل لعدم تضخم الداتا)
        # self.env.cr.execute("""DELETE FROM zk_machine_attendance""")