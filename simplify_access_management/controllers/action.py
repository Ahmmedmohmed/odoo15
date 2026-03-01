# -*- coding: utf-8 -*-

# التعديل الجوهري: استيراد ensure_db و Action و Home من المسار الصحيح لأودو 15
from odoo.addons.web.controllers.main import Home, Action, ensure_db
from odoo.tools.translate import _
from odoo.http import request
from odoo.exceptions import UserError
from odoo import http


class Action(Action):

    @http.route('/web/action/run', type='json', auth="user")
    def run(self, action_id, context=None):
        # تنفيذ الدالة الأصلية
        res = super(Action, self).run(action_id, context)

        if res and isinstance(res, dict):
            # البحث عن إعدادات الوصول للمستخدم والشركة الحالية
            cids = request.httprequest.cookies.get('cids') and request.httprequest.cookies.get('cids').split(',')[
                0] or request.env.company.id

            remove_actions = request.env['remove.action'].sudo().search([
                ('access_management_id.company_ids', 'in', int(cids)),
                ('access_management_id.active', '=', True),
                ('access_management_id.user_ids', 'in', request.env.user.id),
                ('model_id.model', '=', res.get('res_model'))
            ])

            if remove_actions:
                # حذف أنواع الـ Views المحظورة (مثل القائمة أو التقويم) من الاستجابة
                forbidden_views = remove_actions.mapped('view_data_ids.techname')
                if 'views' in res:
                    res['views'] = [v for v in res['views'] if v[1] not in forbidden_views]

        return res

    @http.route('/web/action/load', type='json', auth="user")
    def load(self, action_id, additional_context=None):
        res = super(Action, self).load(action_id, additional_context=additional_context)

        if res and isinstance(res, dict):
            cids = request.httprequest.cookies.get('cids') and request.httprequest.cookies.get('cids').split(',')[
                0] or request.env.company.id

            remove_actions = request.env['remove.action'].sudo().search([
                ('view_data_ids', '!=', False),
                ('access_management_id.company_ids', 'in', int(cids)),
                ('access_management_id.active', '=', True),
                ('access_management_id.user_ids', 'in', request.env.user.id),
                ('model_id.model', '=', res.get('res_model'))
            ])

            if remove_actions:
                forbidden_views = remove_actions.mapped('view_data_ids.techname')
                if 'views' in res:
                    res['views'] = [v for v in res['views'] if v[1] not in forbidden_views]

            # منع الدخول إذا لم يتبق أي واجهة عرض مسموحة
            if 'views' in res and not res.get('views'):
                raise UserError(
                    _("You don't have the permission to access any views. Please contact to administrator."))

        return res


class Home(Home):

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        ensure_db()

        # Odoo 15 Cache Clearing
        request.env.registry.clear_all_caches()

        user = request.env.user.browse(request.session.uid)

        # منطق تعطيل الـ Debug Mode بناءً على صلاحيات المستخدم
        if not kw.get('debug') or kw.get('debug') != "0":
            cids = request.httprequest.cookies.get('cids') and request.httprequest.cookies.get('cids').split(',')[
                0] or request.env.company.id

            # التأكد من تحويل cids لرقم صحيح
            try:
                company_id = int(cids)
            except:
                company_id = request.env.company.id

            access_management = request.env['access.management'].sudo().search([
                ('active', '=', True),
                ('company_ids', 'in', company_id),
                ('disable_debug_mode', '=', True),
                ('user_ids', 'in', user.id)
            ], limit=1)

            if access_management.id:
                # إعادة التوجيه لتعطيل وضع المطور
                return request.redirect('/web?debug=0')

        return super(Home, self).web_client(s_action=s_action, **kw)