# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
# الاستيراد لازم يكون من المسار الرئيسي لويب في نسخة 15
from odoo.addons.web.controllers.main import Export


class Export(Export):

    # في أودو 15، لازم تكرر الـ route هنا بالظبط عشان يتجنب خطأ original_func
    # وبنفس الإعدادات الأصلية للسيرفر
    @http.route('/web/export/get_fields', type='json', auth="user")
    def fields_get(self, model):
        # استدعاء الدالة من الكلاس الأب
        fields = super(Export, self).fields_get(model)

        # منطق إخفاء الحقول الخاص بك
        invisible_field_ids = request.env['hide.field'].sudo().search([
            ('access_management_id.company_ids', 'in', request.env.company.id),
            ('model_id.model', '=', model),
            ('access_management_id.active', '=', True),
            ('access_management_id.user_ids', 'in', request.env.user.id),
            ('invisible', '=', True)
        ])

        if not invisible_field_ids:
            return fields

        hidden_field_names = invisible_field_ids.mapped('field_id.name')

        # تنظيف القائمة المرجعة
        for field_name in list(fields.keys()):
            if field_name in hidden_field_names and field_name != "id":
                del fields[field_name]

        return fields