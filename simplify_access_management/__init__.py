# -*- coding: utf-8 -*-

from . import models
# from . import wizard
from . import controllers

from odoo import api, SUPERUSER_ID


# تعديل uninstall_hook لاستقبال cr و registry
def uninstall_hook(cr, registry):
    # إنشاء env يدويًا في Odoo 15
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['ir.config_parameter'].sudo().search([('key', '=', 'uninstall_check')]).unlink()


# تعديل post_install_action_dup_hook لاستقبال cr و registry
def post_install_action_dup_hook(cr, registry):
    # إنشاء env يدويًا في Odoo 15 لضمان عمل الكود البرمجي بالأسفل
    env = api.Environment(cr, SUPERUSER_ID, {})

    action_data_obj = env['action.data']
    menu_item_obj = env['menu.item']

    # تنفيذ منطق البحث والإنشاء
    for action in env['ir.actions.actions'].sudo().search([]):
        action_data_obj.create({'name': action.name, 'action_id': action.id})

    for menu in env['ir.ui.menu'].sudo().search([]):
        menu_item_obj.create({'name': menu.display_name, 'menu_id': menu.id})