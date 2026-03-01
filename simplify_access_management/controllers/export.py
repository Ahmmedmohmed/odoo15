# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
# استيراد الكلاس الأصلي من main
from odoo.addons.web.controllers.main import Export


class Export(Export):

    # لازم تعيد تعريف الـ route بالكامل هنا عشان Odoo 15 يقدر يربطها صح
    @http.route('/web/export/get_fields', type='json', auth="user")
    def fields_get(self, model):
        # استدعاء الدالة الأصلية باستخدام super
        fields = super(Export, self).fields_get(model)

        # منطق إخفاء الحقول
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

        # تنظيف القائمة
        for field_name in list(fields.keys()):
            if field_name in hidden_field_names and field_name != "id":
                del fields[field_name]

        return fields