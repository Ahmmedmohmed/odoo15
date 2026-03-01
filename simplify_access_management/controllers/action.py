# -*- coding: utf-8 -*-

# الاستيراد الصحيح والمجمع من main لنسخة 15
from odoo.addons.web.controllers.main import Home, Action, ensure_db
from odoo.tools.translate import _
from odoo.http import request
from odoo.exceptions import UserError
from odoo import http


class Action(Action):

    # في Odoo 15، يجب تكرار الـ route بالكامل عند عمل Override
    @http.route('/web/action/run', type='json', auth="user")
    def run(self, action_id, context=None):
        res = super(Action, self).run(action_id, context)

        if isinstance(res, dict) and res.get('res_model'):
            # جلب معرف الشركة من الكوكيز أو البيئة الحالية
            cids = request.httprequest.cookies.get('cids')
            company_id = int(cids.split(',')[0]) if cids else request.env.company.id

            remove_actions = request.env['remove.action'].sudo().search([
                ('access_management_id.company_ids', 'in', company_id),
                ('access_management_id.active', '=', True),
                ('access_management_id.user_ids', 'in', request.env.user.id),
                ('model_id.model', '=', res.get('res_model'))
            ])

            if remove_actions:
                forbidden_views = remove_actions.mapped('view_data_ids.techname')
                if res.get('views'):
                    # تصفية الواجهات (Views) بأسلوب بايثون السريع
                    res['views'] = [v for v in res['views'] if v[1] not in forbidden_views]

        return res

    @http.route('/web/action/load', type='json', auth="user")
    def load(self, action_id, additional_context=None):
        res = super(Action, self).load(action_id, additional_context=additional_context)

        if isinstance(res, dict) and res.get('res_model'):
            cids = request.httprequest.cookies.get('cids')
            company_id = int(cids.split(',')[0]) if cids else request.env.company.id

            remove_actions = request.env['remove.action'].sudo().search([
                ('view_data_ids', '!=', False),
                ('access_management_id.company_ids', 'in', company_id),
                ('access_management_id.active', '=', True),
                ('access_management_id.user_ids', 'in', request.env.user.id),
                ('model_id.model', '=', res.get('res_model'))
            ])

            if remove_actions:
                forbidden_views = remove_actions.mapped('view_data_ids.techname')
                if res.get('views'):
                    res['views'] = [v for v in res['views'] if v[1] not in forbidden_views]

            # التحقق من وجود واجهات متبقية
            if 'views' in res and not res.get('views'):
                raise UserError(_("You don't have permission to access any views. Please contact your administrator."))

        return res


class Home(Home):

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        ensure_db()

        # تنظيف الكاش لضمان تطبيق الصلاحيات الجديدة فوراً
        if request.session.uid:
            request.env.registry.clear_all_caches()

        # التحقق من وجود مستخدم مسجل
        if request.session.uid:
            user = request.env.user.browse(request.session.uid)

            # منع وضع المطور (Debug Mode)
            if kw.get('debug') and kw.get('debug') != "0":
                cids = request.httprequest.cookies.get('cids')
                try:
                    company_id = int(cids.split(',')[0]) if cids else request.env.company.id
                except:
                    company_id = request.env.company.id

                access_management = request.env['access.management'].sudo().search([
                    ('active', '=', True),
                    ('company_ids', 'in', company_id),
                    ('disable_debug_mode', '=', True),
                    ('user_ids', 'in', user.id)
                ], limit=1)

                if access_management:
                    # إعادة التوجيه لتعطيل الـ Debug
                    return request.redirect('/web?debug=0')

        return super(Home, self).web_client(s_action=s_action, **kw)