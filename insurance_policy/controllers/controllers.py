# -*- coding: utf-8 -*-
# from odoo import http


# class InsurancePolicy(http.Controller):
#     @http.route('/insurance_policy/insurance_policy', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/insurance_policy/insurance_policy/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('insurance_policy.listing', {
#             'root': '/insurance_policy/insurance_policy',
#             'objects': http.request.env['insurance_policy.insurance_policy'].search([]),
#         })

#     @http.route('/insurance_policy/insurance_policy/objects/<model("insurance_policy.insurance_policy"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('insurance_policy.object', {
#             'object': obj
#         })
