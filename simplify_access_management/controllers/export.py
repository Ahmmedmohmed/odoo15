# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
# الاستيراد لازم يكون من المسار الرئيسي لويب في نسخة 15
from odoo.addons.web.controllers.main import Export


class Export(Export):

    # في أودو 15، الدالة الافتراضية في الكنترولر اسمها get_fields وليست fields_get
    @http.route('/web/export/get_fields', type='json', auth="user")
    def get_fields(self, model, import_compat=True, **kw):
        # استدعاء الدالة من الكلاس الأب
        fields = super(Export, self).get_fields(model, import_compat=import_compat, **kw)

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
        # الدالة الأصلية في أودو ترجع قائمة من القواميس وليس قاموساً
        filtered_fields = []
        for field in fields:
            field_name = field.get('id')
            if field_name not in hidden_field_names or field_name == "id":
                filtered_fields.append(field)

        return filtered_fields