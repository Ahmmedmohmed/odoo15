""" Initialize Project """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class MaterialPurchaseRequisition(models.Model):
    _inherit = 'material.purchase.requisition'

    project_id = fields.Many2one(
        'project.project',
        string='Project'
    )
    task_id = fields.Many2one(
        'project.task',
        string='Task'
    )
