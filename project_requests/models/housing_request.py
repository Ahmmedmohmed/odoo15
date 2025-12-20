from odoo import fields, api, models


class HousingRequest(models.Model):
    _name = 'housing.request'

    housing = fields.Char(
        string='نوع السكن',
        required=True,
    )
    housing_type = fields.Many2one(
        comodel_name='accommodation.type',
        string='نوع السكن',
        required=True,
    )


    qty = fields.Float(
        string='عدد اﻷفراد',
        required=True,
    )
    note = fields.Char(
        string="ملاحظات"
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
    )
    project_task_id = fields.Many2one(
        'project.task',
        string='Task',
    )

    @api.onchange('fleet_id')
    def onchange_fleet_id(self):
        for rec in self:
            rec.fleet_model_id = rec.fleet_id.model_id.id
