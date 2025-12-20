# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FleetOperations(models.Model):
    """Fleet Operations model."""

    _inherit = 'fleet.vehicle'


    driver_id = fields.Many2one('res.partner', string='Driver')
    vehicle_owner = fields.Many2one('res.partner', string='Vehicle Owner')


    date_and_time = fields.Datetime(default=fields.Datetime.now,string=" التاريخ والوقت")
    vehicle_type = fields.Char(string="نوع المعدة")
    uom_id = fields.Many2one("uom.uom",string="الوحدة")


    # vendor_id = fields.Many2one("res.partner",string=" المورد")
    driver = fields.Char(string="السائق")

    quantity = fields.Integer(string="الكمية ")
    type_of_work = fields.Char(string="طبيعة العمل")
    place = fields.Char(string="المكان")
    notes = fields.Text(string="ملاحظات")
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string='المشرف'
    )


    reviewed = fields.Boolean(string=" تم المراجعة")


    billed_vehicle = fields.Boolean(string=" تم الفوترة ",default=False)


    def action_create_bill_from_vehicle(self):
        for vehicle in self:
            bills = self.env['account.move'].create({
                'move_type': 'in_invoice',
                'partner_id': vehicle.vehicle_owner.partner_id.id,
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': [(0, 0, {
                    'name': vehicle.model_id.id,
                    'quantity': vehicle.quantity,
                })],
            })

            vehicle.billed_vehicle= True


