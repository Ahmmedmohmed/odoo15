# -*- coding: utf-8 -*-
# from odoo import http


# class NileAirAppraisal(http.Controller):
#     @http.route('/nile_air_appraisal/nile_air_appraisal/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nile_air_appraisal/nile_air_appraisal/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('nile_air_appraisal.listing', {
#             'root': '/nile_air_appraisal/nile_air_appraisal',
#             'objects': http.request.env['nile_air_appraisal.nile_air_appraisal'].search([]),
#         })

#     @http.route('/nile_air_appraisal/nile_air_appraisal/objects/<model("nile_air_appraisal.nile_air_appraisal"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nile_air_appraisal.object', {
#             'object': obj
#         })
