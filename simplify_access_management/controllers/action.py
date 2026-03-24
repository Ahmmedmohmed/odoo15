# -*- coding: utf-8 -*-

from odoo.addons.web.controllers.main import Home, Action, ensure_db
from odoo.tools.translate import _
from odoo.http import request
from odoo import http


class Action(Action):

    # التعديل الجوهري: إضافة **kwargs لاستقبال أي متغيرات إضافية يرسلها أودو 15
    @http.route('/web/action/run', type='json', auth="user")
    def run(self, action_id, context=None, **kwargs):
        # تمرير كل المتغيرات للـ super لضمان عدم حدوث TypeError
        res = super(Action, self).run(action_id, context=context, **kwargs)

        if isinstance(res, dict) and res.get('res_model'):
            cids = request.httprequest.cookies.get('cids')
            try:
                company_id = int(cids.split(',')[0]) if cids else request.env.company.id
            except:
                company_id = request.env.company.id

            # البحث في موديل الصلاحيات (Sudo لضمان القراءة)
            remove_actions = request.env['remove.action'].sudo().search([
                ('access_management_id.company_ids', 'in', company_id),
                ('access_management_id.active', '=', True),
                ('access_management_id.user_ids', 'in', request.env.user.id),
                ('model_id.model', '=', res.get('res_model'))
            ])

            if remove_actions:
                forbidden_views = remove_actions.mapped('view_data_ids.techname')
                if res.get('views'):
                    # تصفية الواجهات (Views) التي ليس للمستخدم صلاحية عليها
                    res['views'] = [v for v in res['views'] if v[1] not in forbidden_views]

        return res

    @http.route('/web/action/load', type='json', auth="user")
    def load(self, action_id, additional_context=None, **kwargs):
        # إضافة **kwargs هنا أيضاً لضمان التوافق مع نداءات الـ RPC في V15
        res = super(Action, self).load(action_id, additional_context=additional_context, **kwargs)

        if isinstance(res, dict) and res.get('res_model'):
            cids = request.httprequest.cookies.get('cids')
            try:
                company_id = int(cids.split(',')[0]) if cids else request.env.company.id
            except:
                company_id = request.env.company.id

            remove_actions = request.env['remove.action'].sudo().search([
                ('access_management_id.company_ids', 'in', company_id),
                ('access_management_id.active', '=', True),
                ('access_management_id.user_ids', 'in', request.env.user.id),
                ('model_id.model', '=', res.get('res_model'))
            ])

            if remove_actions:
                forbidden_views = remove_actions.mapped('view_data_ids.techname')
                if res.get('views'):
                    res['views'] = [v for v in res['views'] if v[1] not in forbidden_views]

        return res


class Home(Home):

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        ensure_db()

        # التأكد من هوية المستخدم قبل فحص صلاحيات الـ Debug Mode
        if request.session.uid:
            user = request.env['res.users'].sudo().browse(request.session.uid)

            # إذا حاول المستخدم تفعيل وضع المطور وهو محظور عليه
            if kw.get('debug'):
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
                    # إجباره على العودة للوضع العادي
                    return request.redirect('/web?debug=0')

        return super(Home, self).web_client(s_action=s_action, **kw)