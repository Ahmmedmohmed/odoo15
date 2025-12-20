# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ContractProject(models.Model):
    _inherit = 'project.project'

    def action_open_contract(self):
        print('========= TEST ================')
        order_id = self.env['contract.contract'].sudo()
        views = [(False, 'tree'), (False, 'form')]
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'contract.contract',
                'view_mode': 'form,tree',
                'view_type': 'form',
                'res_id': order_id.id,
                'views': views,
                'target': 'current',
                'domain': [('project_id', '=', rec.id)],
            }

    def action_open_insurance_policy(self):
        order_id = self.env['insurance.policy'].sudo()
        views = [(False, 'tree'), (False, 'form')]
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'insurance.policy',
                'view_mode': 'form,tree',
                'view_type': 'form',
                'res_id': order_id.id,
                'views': views,
                'target': 'current',
                'domain': [('project_id', '=', rec.id)],
            }

    def action_open_tender(self):
        order_id = self.env['tender.request'].sudo()
        views = [(False, 'tree'), (False, 'form')]
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'tender.request',
                'view_mode': 'form,tree',
                'view_type': 'form',
                'res_id': order_id.id,
                'views': views,
                'target': 'current',
                'domain': [('project_id', '=', rec.id)],
            }
