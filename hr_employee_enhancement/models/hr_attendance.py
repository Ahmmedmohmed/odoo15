# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'


    project_id = fields.Many2one(
        comodel_name='project.project',
        string="Project",
    )
