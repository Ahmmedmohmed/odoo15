from odoo import fields, api, models


class CreateContract(models.Model):
    _name = 'create.request'

    product_id = fields.Many2one(
        'product.product',
        string='المنتج',
        required=True
    )
    description = fields.Char(
        string='الوصف',
        required=True
    )
    qty = fields.Float(
        string='الكمية',
        default=1,
        required=True
    )
    qty_on_hand = fields.Float(
        related="product_id.qty_available",
        string="المخزون المتوفر"
    )
    uom = fields.Many2one(
        'uom.uom',
        string='وحدة القياس',
        required=True
    )
    check = fields.Boolean(
        string='تأكيد',
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project'
    )
    tag_ids = fields.Many2many(
        comodel_name="project.tags",
        string="العلامات"
    )
    note = fields.Char(
        string="ملاحظات"
    )
    project_task_id = fields.Many2one(
        'project.task',
        string='Task'
    )

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            rec.description = rec.product_id.name
            rec.uom = rec.product_id.uom_id.id
