# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InsurancePolicy(models.Model):
    _name = 'insurance.policy'
    _description = 'insurance policy'

    insurance_company = fields.Many2one("res.partner")
    customer_id = fields.Many2one("res.partner")
    policy_no = fields.Char(string="Policy No")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    extension_date = fields.Date(string='Extension Date', compute="_compute_new_extension_date")
    contract_no = fields.Char(string='Contract No')
    amount = fields.Float(string="Amount")
    binding_type = fields.Selection([('expired', 'Expired'),
                                     ('running', 'Running')], default='running')
    contract_id = fields.Many2one('contract.contract')
    project_id = fields.Many2one('project.project')
    extension_date_line_ids = fields.One2many('extension.date.line', 'insurance_policy_id',
                                              string="extension date line")

    @api.depends('extension_date_line_ids')
    def _compute_new_extension_date(self):
        for rec in self:
            lines = rec.env['extension.date.line'].sudo().search(
                [('insurance_policy_id', '=', rec.id), ('check', '=', True)])
            if lines:
                rec.extension_date = lines[-1].new_extension_date
            else:
                rec.extension_date = False


class ExtensionDateLine(models.Model):
    _name = 'extension.date.line'
    _description = 'Extension Date Line'

    name = fields.Char(string="name")
    new_extension_date = fields.Date(string="New Extension Date")
    check = fields.Boolean(string="Check")
    insurance_policy_id = fields.Many2one('insurance.policy', string="Insurance Policy")


class ContractApps(models.Model):
    _inherit = "contract.contract"

    def create_insurance_policy(self):
        print('=========== TEST ================')
