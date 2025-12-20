# -*- coding: utf-8 -*-
# from odoo import http


# class ContractProject(http.Controller):
#     @http.route('/contract_project/contract_project', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contract_project/contract_project/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('contract_project.listing', {
#             'root': '/contract_project/contract_project',
#             'objects': http.request.env['contract_project.contract_project'].search([]),
#         })

#     @http.route('/contract_project/contract_project/objects/<model("contract_project.contract_project"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contract_project.object', {
#             'object': obj
#         })
