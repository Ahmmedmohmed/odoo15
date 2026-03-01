# -*- coding: utf-8 -*-
#################################################################################
# Author      : Terabits Technolab (<www.terabits.xyz>)
# Copyright(c): 2021
# All Rights Reserved.
#
# This module is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    "name": "Advanced Web Domain Widget",
    "version": "15.0.1.0.0",  # تم تعديل الإصدار ليتناسب مع 15
    "summary": "Set all relational fields domain by selecting its records using `in, not in` operator.",
    "sequence": 10,
    "author": "Terabits Technolab",
    "license": "OPL-1",
    "website": "https://www.terabits.xyz",
    "description": """
        Advanced Domain Widget for Odoo 15 to select records for Many2one/Many2many 
        fields directly in domain selector.
    """,
    "price": 29.00,
    "currency": "USD",
    "depends": ["base", "web"],
    "data": [
        # في أودو 15 نفضل أحياناً استدعاء ملفات الـ XML الخاصة بالـ Templates هنا
        # إذا لم يتم تعريفها في الـ Assets بشكل صحيح
    ],
    "assets": {
        # أصول الواجهة الخلفية (Backend)
        "web.assets_backend": [
            "advanced_web_domain_widget/static/src/core/**/*.js",
            "advanced_web_domain_widget/static/src/core/**/*.scss",
            "advanced_web_domain_widget/static/src/dateSelectionBits/dateSelectionBits.js",
            "advanced_web_domain_widget/static/src/fields/domain/domain_field.js",
            # إضافة ملفات الـ SCSS الخاصة بالـ Domain Selector
            "advanced_web_domain_widget/static/src/scss/domain_selector.scss",
        ],
        # تعريف الـ QWeb Templates (مهم جداً في أودو 15)
        "web.assets_qweb": [
            "advanced_web_domain_widget/static/src/core/**/*.xml",
            "advanced_web_domain_widget/static/src/dateSelectionBits/dateSelectionBits.xml",
            "advanced_web_domain_widget/static/src/fields/domain/domain_field.xml",
        ],
    },
    "images": ["static/description/banner.png"],
    "application": True,
    "installable": True,
    "auto_install": False,
}