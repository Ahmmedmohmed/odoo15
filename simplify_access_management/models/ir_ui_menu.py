from odoo import fields, models, api, _
from odoo.http import request


class ir_ui_menu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # 1. جلب النتيجة العادية من غير count الأول عشان نقدر نفلترها
        ids = super(ir_ui_menu, self).search(args, offset=0, limit=None, order=order, count=False)
        user = self.env.user

        # 2. تأمين قراءة الكوكيز (عشان لو الكود شغال في الخلفية Cron Job مايضربش إيرور)
        if request and hasattr(request, 'httprequest') and request.httprequest.cookies.get('cids'):
            cids = request.httprequest.cookies.get('cids').split(',')[0]
        else:
            cids = self.env.company.id

        # 3. فلترة القوائم الممنوعة
        for menu_id in user.access_management_ids.filtered(lambda line: int(cids) in line.company_ids.ids).mapped(
                'hide_menu_ids.menu_id'):
            menu_id = self.browse(menu_id)
            if menu_id in ids:
                ids = ids - menu_id

        # 4. تطبيق الـ limit والـ offset بعد الفلترة
        if offset:
            ids = ids[offset:]
        if limit:
            ids = ids[:limit]

        # 5. التعديل الأهم لـ Odoo 15: إرجاع العدد لو تم طلب count، أو إرجاع الـ Recordset
        return len(ids) if count else ids

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ir_ui_menu, self).create(vals_list)
        menu_item_obj = self.env['menu.item']
        for record in res:
            menu_item_obj.create({'name': record.display_name, 'menu_id': record.id})
        return res

    def unlink(self):
        menu_item_obj = self.env['menu.item']
        for record in self:
            menu_item_obj.search([('menu_id', '=', record.id)]).unlink()
        return super(ir_ui_menu, self).unlink()