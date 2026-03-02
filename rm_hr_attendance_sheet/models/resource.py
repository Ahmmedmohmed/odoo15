# -*- coding: utf-8 -*-

import pytz
from operator import itemgetter
from odoo import api, fields, models, _


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    def _attendance_intervals(self, start_dt, end_dt, resource=None, domain=None, tz=None):
        """
        تحسين الدالة لتتوافق مع هيكلية Odoo 15
        حيث تعتمد النسخة 15 على _attendance_intervals_batch بشكل أساسي
        """
        if resource is None:
            resource = self.env['resource.resource']

        # في Odoo 15، الدالة _attendance_intervals_batch هي الطريقة القياسية للحصول على الفترات
        intervals = self._attendance_intervals_batch(
            start_dt, end_dt, resources=resource, domain=domain, tz=tz
        )
        return intervals[resource.id]

    def att_get_work_intervals(self, sheet, day_start, day_end, tz):
        """
        تحويل الفترات الزمنية من التوقيت المحلي للموظف إلى UTC
        لضمان دقة حسابات التأخير والإضافي في Odoo 15
        """
        # إضافة المنطقة الزمنية للتواريخ المدخلة لضمان دقة العمليات الحسابية
        day_start = day_start.replace(tzinfo=tz)
        day_end = day_end.replace(tzinfo=tz)

        # استدعاء فترات الحضور المجدولة للموظف
        attendance_intervals = self._attendance_intervals(day_start, day_end, tz=tz)
        working_intervals = []

        for interval in attendance_intervals:
            # تحويل الفترات إلى UTC مع إزالة معلومات المنطقة الزمنية للتخزين
            working_interval_tz = (
                interval[0].astimezone(pytz.UTC).replace(tzinfo=None),
                interval[1].astimezone(pytz.UTC).replace(tzinfo=None)
            )
            working_intervals.append(working_interval_tz)

        # تنظيف الفترات ودمج المتداخل منها
        clean_work_intervals = self.att_interval_clean(working_intervals)
        return clean_work_intervals

    def att_interval_clean(self, intervals):
        """ ترتيب ودمج الفترات المتداخلة لضمان عدم تكرار ساعات العمل """
        if not intervals:
            return []
        intervals = sorted(intervals, key=itemgetter(0))
        cleaned = []
        working_interval = None
        for current_interval in intervals:
            if not working_interval:
                working_interval = [current_interval[0], current_interval[1]]
            elif working_interval[1] < current_interval[0]:
                cleaned.append(tuple(working_interval))
                working_interval = [current_interval[0], current_interval[1]]
            elif working_interval[1] < current_interval[1]:
                working_interval[1] = current_interval[1]
        if working_interval:
            cleaned.append(tuple(working_interval))
        return cleaned

    def att_interval_without_leaves(self, interval, leave_intervals):
        """ استبعاد فترات الإجازات من فترات العمل المجدولة لحساب صافي ساعات الحضور """
        if not interval:
            return []
        if leave_intervals is None:
            leave_intervals = []
        intervals = []
        leave_intervals = self.att_interval_clean(leave_intervals)
        current_interval = [interval[0], interval[1]]
        for leave in leave_intervals:
            if leave[1] <= current_interval[0]:
                continue
            if leave[0] >= current_interval[1]:
                break
            if current_interval[0] < leave[0] < current_interval[1]:
                current_interval[1] = leave[0]
                intervals.append((current_interval[0], current_interval[1]))
                current_interval = [leave[1], interval[1]]
            if current_interval[0] <= leave[1]:
                current_interval[0] = leave[1]
        if current_interval and current_interval[0] < interval[1]:
            intervals.append((current_interval[0], current_interval[1]))
        return intervals