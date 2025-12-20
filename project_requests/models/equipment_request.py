from odoo import fields, api, models


class EquipmentRequest(models.Model):
    _name = 'equipment.request'

    description = fields.Char(
        # required=True
    )
    fleet_id = fields.Many2one(
        'fleet.vehicle',
        string=' المعدة'
    )
    fleet_model_id = fields.Many2one(
        'fleet.vehicle.model',
        string='الموديل'
    )
    qty = fields.Float(
        string='العدد المطلوب',
        required=True,
    )
    tag_ids = fields.Many2many(
        comodel_name="project.tags",
        string="العلامات"
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
    supplier_id = fields.Many2one(
        'res.partner',
        string='المورد'
    )

    vehicle_type_id = fields.Many2one(
        'vehicle.type',
        string='Vehicle Type',
        required=True,
    )

    # from_request_work = fields.Boolean(default=False)

    @api.onchange('fleet_id')
    def onchange_fleet_id(self):
        for rec in self:
            rec.fleet_model_id = rec.fleet_id.model_id.id
