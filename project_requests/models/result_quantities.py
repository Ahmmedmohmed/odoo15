from odoo import fields, api, models


class ResultQuantities(models.Model):
    _name = 'result.quantities'

    type = fields.Char(
        string='نوع المشون',
        required=True
    )
    cumulative_quantity = fields.Float(
        string='الكمية التراكمية لناتج الكسارة حتي تاريخه (م3)',
        required=True
    )
    current_cumulative_quantity = fields.Float(
        string='كمية اليوم الحالي المسحوبة من المشون (م3)',
        required=True
    )
    internal_remaining_quantity = fields.Float(
        string='الكمية التراكمية المسحوبة من المشون حتي تاريخه (م3)',
        required=True
    )
    remaining_quantity = fields.Float(
        string='الكمية المتبية بالمشون حتي تاريخه (م3)',
        required=True
    )
    note = fields.Text(
        string="ملاحظات"
    )
    result_project_follow_id = fields.Many2one(
        'project.follow'
    )
