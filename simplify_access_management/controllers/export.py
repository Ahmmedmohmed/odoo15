# -*- coding: utf-8 -*-

from odoo import http
from odoo.exceptions import UserError
# التعديل هنا: استيراد Export من main بدلاً من export
from odoo.addons.web.controllers.main import Export
from odoo.http import request


class Export(Export):

    @http.route('/web/export/get_fields', type='json', auth="user")
    def fields_get(self, model):
        # تنفيذ الدالة الأصلية لجلب الحقول
        fields = super(Export, self).fields_get(model)

        # جلب الحقول المحظورة لهذا المستخدم والشركة الحالية
        # ملاحظة: تم إضافة .sudo() لضمان جلب قواعد البيانات حتى لو المستخدم صلاحياته محدودة
        invisible_field_ids = request.env['hide.field'].sudo().search([
            ('access_management_id.company_ids', 'in', request.env.company.id),
            ('model_id.model', '=', model),
            ('access_management_id.active', '=', True),
            ('access_management_id.user_ids', 'in', request.env.user.id),
            ('invisible', '=', True)
        ])

        if not invisible_field_ids:
            return fields

        # استخراج أسماء الحقول المخفية لتقليل عدد اللفات داخل اللوب
        hidden_field_names = invisible_field_ids.mapped('field_id.name')

        # تنظيف قائمة الحقول المتاحة للتصدير
        for field_name in list(fields.keys()):
            if field_name in hidden_field_names and field_name != "id":
                del fields[field_name]

        return fields