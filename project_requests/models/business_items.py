from odoo import fields, api, models, _
from odoo.exceptions import UserError, ValidationError, Warning


class BusinessItems(models.Model):
    _name = 'business.items'

    product_id = fields.Many2one(
        'product.product',
        string='البند',
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
    uom = fields.Many2one(
        'uom.uom',
        string='وحدة القياس',
        required=True
    )
    price = fields.Float(
        string="السعر"
    )
    total_price = fields.Float(
        string="السعر الكلي",
        compute='compute_total_price'
    )
    project_id = fields.Many2one(
        'project.project'
    )
    project_task_id = fields.Many2one(
        'project.task'
    )

    @api.constrains('qty', 'price')
    def _check_quantities(self):
        for rec in self:
            if rec.qty < 0:
                raise ValidationError(_('الكمية يجب ان لا تكون أقل من صفر'))
            if rec.price < 0:
                raise ValidationError(_('السعر يجب ان لا تكون أقل من صفر'))

    @api.depends('qty', 'price')
    def compute_total_price(self):
        for rec in self:
            rec.total_price = rec.qty * rec.price

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            rec.description = rec.product_id.name
            rec.uom = rec.product_id.uom_id.id
