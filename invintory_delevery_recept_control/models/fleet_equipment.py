# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


class FleetEquipment(models.Model):
    _name = 'fleet.equipment'
    _description = 'fleet.equipment'
    _rec_name = 'fleet_id'

    date_and_time = fields.Datetime(default=fields.Datetime.now, string=" التاريخ والوقت")
    fleet_id = fields.Many2one("fleet.vehicle",required=True, string=" المعدة")
    vendor_id = fields.Many2one("res.partner",
                                string=" المورد",
                                )

    driver_id = fields.Many2one(comodel_name='res.partner',
                                string='السائق',
                                related='fleet_id.driver_id',
                                readonly=False)
    vehicle_owner = fields.Many2one('res.partner',
                                    string='Vehicle Owner'
                                    ,required=True,
                                    related='fleet_id.vehicle_owner',
                                    readonly=False)
    uom_id = fields.Many2one("uom.uom", string="الوحدة")
    quantity = fields.Integer(string="الكمية ")
    type_of_work = fields.Char(string="طبيعة العمل")
    place = fields.Char(string="المكان")
    notes = fields.Text(string="ملاحظات")
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string='المشرف'
    )

    reviewed = fields.Boolean(string=" تم المراجعة")

    billed_equipment = fields.Boolean(string=" تم الفوترة ", default=False)
    record_bill_state = fields.Selection([('not_billed','Not Billed'),
                                          ('billed','Billed'),],default='not_billed',copy=False)

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))

    #
    def action_create_bill_from_fleet_equipment(self):
        vendor_dict = {}
        for record in self:
            if record.record_bill_state == 'not_billed':
                vendor = record.vehicle_owner
                if vendor:
                    if vendor not in vendor_dict:
                        vendor_dict[vendor] = []
                    vendor_dict[vendor].append(record)
        created_bills = self.env['account.move']

        for vendor, records in vendor_dict.items():
            invoice_lines = []
            for record in records:
                invoice_lines.append((0, 0, {
                    'name': record.fleet_id.name,
                    'quantity': record.quantity,
                }))
                record.write({'record_bill_state': 'billed'})
            bill = self.env['account.move'].create({
                'move_type': 'in_invoice',
                'partner_id': vendor.id,
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': invoice_lines,
            })
            created_bills += bill

        return created_bills
            # billed_record.write({'billed_equipment': True})





    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fleet.equipment') or _('New')
        return super(FleetEquipment, self).create(vals)

    def re_sequence_equ_record_records(self):
        """Re-sequence all records using ir.sequence"""
        # Fetch all records ordered by creation date
        records = self.env['fleet.equipment'].search([], order='create_date ASC')
        for r in records:
            r.name = ""

        # Track already used sequences to avoid duplicates
        existing_sequences = set(records.mapped('name'))

        for record in records:
            # Skip if record already has a valid sequence (not 'New' or empty)
            if record.name and record.name != _('New') and record.name != 'New':
                continue

            # Generate new sequence
            new_sequence = self.env['ir.sequence'].next_by_code('fleet.equipment')

            # Make sure we don't create duplicates
            while new_sequence in existing_sequences:
                new_sequence = self.env['ir.sequence'].next_by_code('fleet.equipment')

            # Update record
            record.write({'name': new_sequence})
            existing_sequences.add(new_sequence)

            # _logger.info(f"Updated record ID {record.id} with sequence {new_sequence}")

        return True

