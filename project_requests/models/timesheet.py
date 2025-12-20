
from odoo import fields, models, api, _


class Timesheet(models.Model):
    _inherit = "account.analytic.line"

    days_spent = fields.Integer(
        'Days Spent'
    )

    project_task_id = fields.Many2one(
        'project.task'
    )
    project_id = fields.Many2one(
        'project.project'
    )
