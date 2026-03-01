# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _


class BaseModel(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        # تنفيذ عملية البحث الأصلية لجلب السجلات
        res = super(BaseModel, self).search_read(domain, fields, offset, limit, order, **read_kwargs)

        # إذا تم استدعاء البحث من أداة الـ Domain المتقدمة وكان الموديل يدعم الشركات
        if self._context.get('web_domain_widget') and hasattr(self, 'company_id'):
            for rec in res:
                # جلب اسم الشركة وإضافته للبيانات المعادة للواجهة (JS)
                record_id = rec.get('id')
                if record_id:
                    company = self.browse(record_id).company_id
                    rec.update({'company_name': company.name if company else ''})

        return res