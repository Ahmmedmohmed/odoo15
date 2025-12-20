from odoo import fields, api, models


class ExecutedWorks(models.Model):
    _name = 'executed.works'

    product_id = fields.Many2one(
        'product.product',
        string='البند'
    )
    uom = fields.Many2one(
        'uom.uom',
        string='وحدة القياس'
    )
    basic_quantity = fields.Float(
        string='الكمية اﻷساسية'
    )
    related_product_id = fields.Many2one(
        string='البند',
        related='product_id'
    )
    related_uom = fields.Many2one(
        string='وحدة القياس',
        related='uom'
    )
    related_basic_quantity = fields.Float(
        string='الكمية اﻷساسية',
        related='basic_quantity'
    )
    executed_quantity = fields.Float(
        string='الكمية المنفذة (ضهر عربية) لليوم الحالي (م3)',
        related='executed_project_follow_id.exchange_quantity'
        ,readonly=False
    )
    ratio = fields.Float(
        string='النسبة'
    )
    current_quantity = fields.Float(
        string='الكمية المنفذة (هندسي + تقديري) لليوم الحالي (م3)',
        # compute='compute_values'
    )
    cumulative_executed_quantity = fields.Float(
        string='الكمية المنفذة (ضهر عربية) تراكمية (م3)',
        related='executed_project_follow_id.cumulative_exchange_quantity'
    )
    cumulative_quantity = fields.Float(
        string='الكمية المنفذة (هندسى) تراكمية (م3)',
        # compute='compute_values'
    )
    rate = fields.Float(
        string='% نسبة الهالك',
        compute='compute_values',
        digits=(5, 2)
    )
    note = fields.Text(
        string="ملاحظات"
    )
    executed_project_follow_id = fields.Many2one(
        'project.follow'
    )

    def compute_values(self):
        for rec in self:
            # if rec.ratio and rec.ratio > 0:
            #     rec.current_quantity = rec.executed_quantity - (rec.executed_quantity * rec.ratio)
            #     rec.cumulative_quantity = rec.cumulative_executed_quantity -
            #                               (rec.cumulative_executed_quantity * rec.ratio)
            # else:
            #     rec.current_quantity = rec.executed_quantity
            #     rec.cumulative_quantity = rec.cumulative_executed_quantity
            if rec.cumulative_quantity > 0:
                rec.rate = (rec.cumulative_executed_quantity / rec.cumulative_quantity) - 1
            else:
                rec.rate = 1

    @api.model
    def create(self, vals):
        res = super(ExecutedWorks, self).create(vals)
        # Post message to parent
        if res.executed_project_follow_id:
            body = f"Line added: {res.product_id.name} "
            res.executed_project_follow_id.message_post(body=body)
        return res

    def write(self, vals):
        # Track changes before write
        for record in self:
            old_values = {
                'product_id': record.product_id.name if record.product_id else False,
                'executed_quantity': record.executed_quantity,
                'current_quantity': record.current_quantity,
                'cumulative_quantity': record.cumulative_quantity,
            }

        res = super(ExecutedWorks, self).write(vals)

        # Post changes to parent
        for record in self:
            changes = []
            if 'product_id' in vals and old_values['product_id'] != record.product_id.name:
                changes.append(f"Product: {old_values['product_id']} → {record.product_id.name}")
            if 'executed_quantity' in vals and old_values['executed_quantity'] != record.executed_quantity:
                changes.append(f"Executed Quantity: {old_values['executed_quantity']} → {record.executed_quantity}")
            if 'current_quantity' in vals and old_values['current_quantity'] != record.current_quantity:
                changes.append(f"Current Quantity: {old_values['current_quantity']} → {record.current_quantity}")
            if 'cumulative_quantity' in vals and old_values['cumulative_quantity'] != record.cumulative_quantity:
                changes.append(f"Cumulative Quantity: {old_values['cumulative_quantity']} → {record.cumulative_quantity}")

            if changes and record.executed_project_follow_id:
                body = "Line updated:<br/>" + "<br/>".join(changes)
                record.executed_project_follow_id.message_post(body=body)

        return res

    def unlink(self):
        # Track deletion
        for record in self:
            if record.executed_project_follow_id:
                body = f"Line deleted: {record.product_id.name} "
                record.executed_project_follow_id.message_post(body=body)
        return super(ExecutedWorks, self).unlink()
