from odoo import fields, api, models


class RemainingQuantities(models.Model):
    _name = 'remaining.quantities'

    type = fields.Char(
        string='نوع المشون',
        required=True
    )
    cumulative_quantity = fields.Float(
        string='الكمية التراكمية الموردة بالمشون حتي تاريخه',
        required=True
    )
    internal_cumulative_quantity = fields.Float(
        string='كمية التوريد الداخلي التراكمية حتي تاريخه (م3)',
        required=True
    )
    remaining_quantity = fields.Float(
        string='الكمية المتبقية بالمشون حتي تاريخه (م3)',
        required=True
    )
    note = fields.Text(
        string="ملاحظات"
    )
    remaining_project_follow_id = fields.Many2one(
        'project.follow'
    )
