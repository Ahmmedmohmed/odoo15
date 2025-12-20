from odoo import fields, api, models, _
from odoo.exceptions import UserError, ValidationError, Warning


class DailySupplies(models.Model):
    _name = 'daily.supplies'

    product_id = fields.Many2one(
        'product.product',
        string='نوع التوريد'
    )
    basic_quantity = fields.Float(
        string='الكمية اﻷساسية'
    )
    related_product_id = fields.Many2one(
        string='نوع التوريد',
        related='product_id'
    )
    related_basic_quantity = fields.Float(
        string='الكمية اﻷساسية',
        related='basic_quantity'
    )
    assay_quantity = fields.Float(
        string='كمية المقايسة'
    )
    current_quantity = fields.Float(
        string='كمية اليوم الحالي (م3)'
    )
    cumulative_quantity = fields.Float(
        string='الكمية التراكمية حتي تاريخه (م3)',
        readonly=1
    )
    exchange_quantity = fields.Float(
        string='كمية الصرف اليومية (م3)'
    )
    cumulative_exchange_quantity = fields.Float(
        string='كمية الصرف التراكمية حتي تاريخه (م3)',
        readonly=1
    )
    remaining_quantity = fields.Float(
        string='الكمية المتبقية بالمشون حتي تاريخه (م3)',
        compute='compute_remaining_quantity'
    )
    note = fields.Text(
        string="ملاحظات"
    )
    daily_project_follow_id = fields.Many2one(
        'project.follow'
    )

    @api.constrains('current_quantity', 'assay_quantity', 'exchange_quantity')
    def _check_quantities(self):
        for rec in self:
            if rec.current_quantity < 0:
                raise ValidationError(_('كمية اليوم الحالي يجب ان لا تكون أقل من صفر'))
            if rec.assay_quantity < 0:
                raise ValidationError(_('كمية المقايسة يجب ان لا تكون أقل من صفر'))
            if rec.exchange_quantity < 0:
                raise ValidationError(_('كمية الصرف اليومية يجب ان لا تكون أقل من صفر'))

    @api.depends('cumulative_quantity', 'cumulative_exchange_quantity')
    def compute_remaining_quantity(self):
        for rec in self:
            rec.remaining_quantity = rec.cumulative_quantity - rec.cumulative_exchange_quantity

    @api.model
    def create(self, vals):
        res = super(DailySupplies, self).create(vals)
        project_follow_records = self.env['project.follow'].search([
            ('project_id', '=', res.daily_project_follow_id.project_id.id)
        ])
        res.cumulative_quantity = sum(project_follow_records.mapped('daily_supplies_id.current_quantity'))
        res.cumulative_exchange_quantity = sum(project_follow_records.mapped('daily_supplies_id.exchange_quantity'))

        if res.daily_project_follow_id:
            body = (
                f"Supply Line added with "
                f"Assay Quantity: {res.assay_quantity}\n"
                f" and Current Quantity: {res.current_quantity}\n"
                f"and Exchange Quantity: {res.exchange_quantity}\n"
            )
            res.daily_project_follow_id.message_post(body=body)
        return res

    def write(self, vals):
        for record in self:
            old_values = {
                'product_id': record.product_id.name if record.product_id else False,
                'assay_quantity': record.assay_quantity,
                'current_quantity': record.current_quantity,
                'exchange_quantity': record.exchange_quantity,
            }

        res = super(DailySupplies, self).write(vals)
        project_follow_records = self.env['project.follow'].search([
            ('project_id', '=', self.daily_project_follow_id.project_id.id)
        ])
        if vals.get('current_quantity'):
            self.cumulative_quantity = sum(project_follow_records.mapped('daily_supplies_id.current_quantity'))
        if vals.get('exchange_quantity'):
            self.cumulative_exchange_quantity = sum(project_follow_records.mapped('daily_supplies_id.exchange_quantity'))

            # Post changes to parent
        for record in self:
            changes = []
            if 'product_id' in vals and old_values['product_id'] != record.product_id.name:
                changes.append(f"Product: {old_values['product_id']} → {record.product_id.name}")
            if 'assay_quantity' in vals and old_values['assay_quantity'] != record.assay_quantity:
                changes.append(f"assay_quantity: {old_values['assay_quantity']} → {record.assay_quantity}")
            if 'current_quantity' in vals and old_values['current_quantity'] != record.current_quantity:
                changes.append(f"current_quantity: {old_values['current_quantity']} → {record.current_quantity}")
            if 'exchange_quantity' in vals and old_values['exchange_quantity'] != record.exchange_quantity:
                changes.append(f"exchange_quantity: {old_values['exchange_quantity']} → {record.exchange_quantity}")


            if changes and record.daily_project_follow_id:
                    body = "Line updated:<br/>" + "<br/>".join(changes)
                    record.daily_project_follow_id.message_post(body=body)
        return res

    def unlink(self):
        # Track deletion
        for record in self:
            if record.daily_project_follow_id:
                body = f"Line deleted: {record.product_id.name} "
                record.daily_project_follow_id.message_post(body=body)
        return super(DailySupplies, self).unlink()
