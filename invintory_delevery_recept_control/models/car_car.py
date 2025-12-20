# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class CarCar(models.Model):
    _name = 'car.car'
    _description = 'car'
    _rec_name = 'car_type'

    date_and_time = fields.Datetime(default=fields.Datetime.now,string=" التاريخ والوقت")
    car_type = fields.Char(string="نوع السيارة")
    vendor_id = fields.Many2one("res.partner",string=" المورد")
    driver = fields.Char(string="السائق")
    uom_id = fields.Many2one("uom.uom",string="الوحدة")
    quantity = fields.Integer(string="الكمية ")
    meter_reading_start = fields.Float(string="سجل قراءة عداد اول")
    meter_reading_end = fields.Float(string=" سجل قراءة عداد اخر")
    total_meter_reading_km = fields.Float(string="عدد الكيلو متر ")
    payload_type = fields.Char(string=" طبيعة الحمولة")
    move_from = fields.Char(string="من  ")
    move_to = fields.Char(string="الي ")

    billed_cars = fields.Boolean(string=" تم الفوترة ",default=False)
    record_bill_state = fields.Selection([('not_billed','Not Billed'),
                                          ('billed','Billed'),],default='not_billed',copy=False)

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))


    #
    # def action_create_bill_from_cars(self):
    #     for car in self:
    #         bills = self.env['account.move'].create({
    #             'move_type': 'in_invoice',
    #             'partner_id': car.vendor_id.id,
    #             'invoice_date': fields.Date.today(),
    #             'invoice_line_ids': [(0, 0, {
    #                 'name': car.car_type,
    #                 'quantity': car.quantity,
    #             })],
    #         })
    #
    #         car.billed_cars= True



    # def action_create_bill_from_cars(self):
    #     #Group records by vendor
    #     vendor_dict = {}
    #     for record in self:
    #
    #         if record.record_bill_state == 'not_billed':
    #             vendor = record.vendor_id
    #             if vendor not in vendor_dict:
    #                 vendor_dict[vendor] = []
    #             vendor_dict[vendor].append(record)
    #         #Create bills for each vendor
    #     created_bills = self.env['account.move']
    #     for vendor, records in vendor_dict.items():
    #         # Prepare invoice lines for this vendor
    #         invoice_lines = []
    #         for record in records:
    #             invoice_lines.append((0, 0, {
    #                 'name': record.car_type,
    #                 'quantity': record.quantity,
    #             }))
    #             record.write({
    #                 'billed_cars': True,
    #                 'record_bill_state': 'billed'
    #             })
    #
    #         # Create the bill
    #
    #         bill = self.env['account.move'].create({
    #             'move_type': 'in_invoice',
    #             'partner_id': vendor.id,
    #             'invoice_date': fields.Date.today(),
    #             'invoice_line_ids': invoice_lines,
    #         })
    #         created_bills += bill
    #     return created_bills

    def action_create_bill_from_cars(self):
        vendor_dict = {}
        for record in self:
            if record.record_bill_state == 'not_billed':
                vendor = record.vendor_id
                if vendor not in vendor_dict:
                    vendor_dict[vendor] = []
                vendor_dict[vendor].append(record)

        created_bills = self.env['account.move']
        for vendor, records in vendor_dict.items():
            # New: Consolidate by car_type (product)
            product_qty_map = {}
            for record in records:
                key = record.car_type  # Or record.product_id.id if using products
                if key not in product_qty_map:
                    product_qty_map[key] = {
                        "quantity": 0,
                        "record_names": [],
                        # Add other needed fields for the line here!
                    }
                product_qty_map[key]["quantity"] += record.quantity

                # Mark record as billed
                record.write({
                    'billed_cars': True,
                    'record_bill_state': 'billed'
                })

            invoice_lines = []
            for car_type, info in product_qty_map.items():
                invoice_lines.append((0, 0, {
                    'name': car_type,  # Or get product display name as needed
                    'quantity': info['quantity'],
                    # Put any other required line fields here
                }))

            bill = self.env['account.move'].create({
                'move_type': 'in_invoice',
                'partner_id': vendor.id,
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': invoice_lines,
            })
            created_bills += bill
        return created_bills



    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('car.car') or _('New')
        return super(CarCar, self).create(vals)

    def re_sequence_car_record_records(self):
        """Re-sequence all records using ir.sequence"""
        # Fetch all records ordered by creation date
        records = self.env['car.car'].search([], order='create_date ASC')
        for r in records:
            r.name = ""

        # Track already used sequences to avoid duplicates
        existing_sequences = set(records.mapped('name'))

        for record in records:
            # Skip if record already has a valid sequence (not 'New' or empty)
            if record.name and record.name != _('New') and record.name != 'New':
                continue

            # Generate new sequence
            new_sequence = self.env['ir.sequence'].next_by_code('car.car')

            # Make sure we don't create duplicates
            while new_sequence in existing_sequences:
                new_sequence = self.env['ir.sequence'].next_by_code('car.car')

            # Update record
            record.write({'name': new_sequence})
            existing_sequences.add(new_sequence)

            # _logger.info(f"Updated record ID {record.id} with sequence {new_sequence}")

        return True


