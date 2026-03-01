# -*- coding: utf-8 -*-
#################################################################################
# Author      : Terabits Technolab (<www.terabits.xyz>)
# Copyright(c): 2021-23
# All Rights Reserved.
#
# This module is copyright property of the author mentioned above.
# You can't redistribute/reshare/recreate it for any purpose.
#
#################################################################################

{
    'name': 'Simplify Access Management',
    'version': '15.0.4.3.2', # تم تعديل النسخة هنا لتتوافق مع أودو 15
    'sequence': 5,
    'author': 'Terabits Technolab',
    'license': 'OPL-1',
    'category': 'Tools',
    'website': 'https://www.terabits.xyz/r/SNS',
    'summary': """All In One Access Management App for setting the correct access rights for fields, models, menus, views for any module and for any user.""",
    'description': """
        All In One Access Management App for setting the correct access rights for fields, models, menus, views for any module and for any user.
        Configuring correct access rights in Odoo is quite technical for someone who has little experience with the system and can get messy if you are not sure what you are doing. This module helps you avoid all this complexity by providing you with a user friendly interface from where you can define access to specific objects in one place.
    """,
    "images": ["static/description/banner.gif"],
    "price": "370.99",
    "currency": "USD",
    'data': [
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'data/view_data.xml',
        'views/access_management_view.xml',
        'views/res_users_view.xml',
        'views/store_model_nodes_view.xml',
    ],
    # طريقة تعريف الـ assets دي مدعومة في 15، فمش هنغير الـ syntax بتاعها
    'assets': {
        'web.assets_backend': [
            '/simplify_access_management/static/src/js/action_menus.js',
            '/simplify_access_management/static/src/js/hide_chatter.js',
            '/simplify_access_management/static/src/js/cog_menu.js',
            '/simplify_access_management/static/src/js/form_controller.js',
            '/simplify_access_management/static/src/js/pivot_grp_menu.js',
            '/simplify_access_management/static/src/js/model_field_selector.js',
        ],
    },
    'depends': ['web', 'advanced_web_domain_widget'],
    'post_init_hook': 'post_install_action_dup_hook',
    'application': True,
    'installable': True,
    'auto_install': False,
    'live_test_url': 'https://www.terabits.xyz/request_demo?source=index&version=15&app=simplify_access_management',
}