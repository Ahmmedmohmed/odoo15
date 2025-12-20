# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError
from odoo.tools.populate import compute


class StockPicking(models.Model):
    _inherit = 'stock.picking'


    project_id = fields.Many2one(
        'project.project',
        compute='_compute_project_id',
        store=True

    )
    work_shift = fields.Char(
        string='وردية'
    )

    product_id = fields.Many2one(
        comodel_name="product.product",
        compute="_compute_product_name",
        string='الحمولة'
    )



    transfer_numbers = fields.Float(
        string='عدد النقلات'
    )

    manager = fields.Char(
        string='المشرف'
    )
    under_cube = fields.Float(
        string='تحت التكعيب'
    )

    #####################################################################D

    site_number = fields.Char(
        string='رقم بون الموقع'
    )

    quarry_number = fields.Char(
        string='رقم بون المحجر'
    )
    water_number = fields.Char(
        string='رقم البون المائي'
    )

    vehicle_number = fields.Char(
        string='رقم السيارة'
    )

    cube = fields.Float(
        'تكعيب'
    )

    transaction_from = fields.Char(
        string=' مكان التحميل '
    )

    aging_in = fields.Char(
        'مكان التعتيق'
    )

    distance = fields.Float(
        string='مسافة النقل'
    )

    quantity = fields.Integer(
        string='الكمية ',
        compute="compute_quantity_from_line"
    )

    deduct_quantity = fields.Integer(
        string='خصم '
    )

    net_quantity = fields.Integer(
        string='صافبي الكمية '
    )

    quality_and_quantity = fields.Integer(
        string=' ميزان'
    )
    deduction_reason = fields.Text(
        string=' سبب الخصم '
    )


    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string='المشرف'
    )

    notes = fields.Text(string="ملاحظات")

    reviewed = fields.Boolean(string=" تم المراجعة")

    billed_picking = fields.Boolean(string=" تم الفوترة ",default=False)
    record_bill_state = fields.Selection([('not_billed','Not Billed'),
                                          ('billed','Billed'),],default='not_billed',copy=False)


    # quality_and_quantity = fields.Text(
    #     string=' ميزان'
    # )

    loader_type = fields.Char(string='لودر تحميل')
    loader_owner = fields.Many2one(comodel_name='res.partner',
                                   string="صاحب اللودر")



    #####################################################################D

    @api.depends('move_ids_without_package.product_uom_qty')
    def compute_quantity_from_line(self):
        for picking in self:
            if picking.move_ids_without_package:
                # take only the first record
                first_move = picking.move_ids_without_package[0]
                picking.quantity = first_move.product_uom_qty
            else:
                picking.quantity = 0.0


    def _compute_project_id(self):
        for rec in self:
            # Check if we're coming from a project's smart button
            if rec._context.get('default_project_id'):
                rec.project_id = rec._context['default_project_id']
            # Check if we're in a stock picking context with purchase order origin
            elif rec._context.get('active_model') == 'stock.picking' and rec.origin:
                purchase_order = self.env['purchase.order'].search([
                    ('name', '=', rec.origin)
                ], limit=1)
                if purchase_order and purchase_order.project_id:
                    rec.project_id = purchase_order.project_id.id
            # Fallback: keep existing value if none of the above applies
            elif not rec.project_id:
                rec.project_id = False

    @api.depends('move_ids_without_package.product_id')
    def _compute_product_name(self):
        for rec in self:
            if rec.move_ids_without_package:
                rec.product_id = rec.move_ids_without_package[0].product_id.id
            else:
                rec.product_id = 0



    def action_create_bill_from_picking(self):
        # Group records by vendor
        vendor_dict = {}
        for record in self:
            if record.record_bill_state == 'not_billed':
                vendor = record.partner_id
                if vendor not in vendor_dict:
                    vendor_dict[vendor] = []
                vendor_dict[vendor].append(record)

        print("vendor_dict", vendor_dict)

        # Create bills for each vendor
        created_bills = self.env['account.move']
        for vendor, records in vendor_dict.items():
            # Group products and sum quantities
            product_dict = {}
            for record in records:
                # Assuming you want to get product from move_ids_without_package
                # You might need to iterate through moves if there are multiple
                for move in record.move_ids_without_package:
                    product = move.product_id
                    if product not in product_dict:
                        product_dict[product] = 0
                    product_dict[product] += move.quantity_done or move.product_uom_qty

            # Prepare invoice lines for this vendor
            invoice_lines = []
            for product, total_qty in product_dict.items():
                invoice_lines.append((0, 0, {
                    'name': product.name,
                    'product_id': product.id,
                    'quantity': total_qty,
                    'price_unit': product.standard_price,  # or use vendor price list
                    'account_id': product.property_account_expense_id.id or product.categ_id.property_account_expense_categ_id.id,
                }))

            print("invoice_lines", invoice_lines)

            # Create the bill only if there are invoice lines
            if invoice_lines:
                bill = self.env['account.move'].create({
                    'move_type': 'in_invoice',
                    'partner_id': vendor.id,
                    'invoice_date': fields.Date.today(),
                    'invoice_line_ids': invoice_lines,
                })
                created_bills += bill

                # Mark records as billed
                for record in records:
                    record.write({
                        'record_bill_state': 'billed'
                    })

        return created_bills






class StockMove(models.Model):
    _inherit = 'stock.move'
    
    custom_requisition_line_id = fields.Many2one(
        'material.purchase.requisition.line',
        string='Requisitions Line',
        copy=True
    )
