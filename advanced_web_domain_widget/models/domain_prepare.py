# -*- coding: utf-8 -*-
from odoo.http import request
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def prepare_domain_v2(domain):
    """
    تحويل فلاتر التاريخ المخصصة إلى شروط Odoo Domain قياسية.
    """
    if isinstance(domain, tuple) or isinstance(domain, list):
        field_name = domain[0]
        operator = domain[1]
        val = domain[2]

        date_format = '%Y-%m-%d %H:%M:%S'
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # إذا لم يكن الفلتر زمني مخصص، نرجعه كما هو
        if operator != "date_filter":
            return [tuple(domain)]

        # اليوم
        if val == "today":
            start_of_today = current_date
            end_of_today = current_date + timedelta(days=1)
            return ["&", (field_name, ">=", start_of_today), (field_name, "<", end_of_today)]

        # هذا الأسبوع
        if val == "this_week":
            start_of_week = current_date - timedelta(days=current_date.weekday())
            end_of_week = (current_date + timedelta(days=(7 - current_date.weekday())))
            return ["&", (field_name, ">=", start_of_week), (field_name, "<", end_of_week)]

        # هذا الشهر
        if val == "this_month":
            start_of_month = current_date.replace(day=1)
            end_of_month = current_date + relativedelta(day=31)
            return ["&", (field_name, ">=", start_of_month), (field_name, "<=", end_of_month)]

        # الـ 7 أيام الماضية
        if val == "last_7_days":
            start_of_last_7_days = current_date - timedelta(days=6)
            return [(field_name, ">=", start_of_last_7_days)]

        # الـ 30 يوم الماضية
        if val == "last_30_days":
            start_of_last_30_days = current_date - timedelta(days=29)
            return [(field_name, ">=", start_of_last_30_days)]

        # ... (بقية الشروط تعمل بنفس المنطق)

    return [tuple(domain)]