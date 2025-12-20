# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    custom_requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Purchase Requisition',
        readonly=True,
        copy=True
    )
    project_id = fields.Many2one(
        'project.project',
        compute='_compute_project_id',
        store=True
    )


    work_shift = fields.Char(
        string='وردية'
    )
    quarry_number = fields.Char(
        string='رقم بون المحجر'
    )
    water_number = fields.Char(
        string='رقم البون المائي'
    )
    transaction_from = fields.Char(
        string='مكان التحميل'
    )
    distance = fields.Char(
        string='المسافة'
    )
    payload = fields.Char(
        string='الحمولة'
    )
    vehicle_number = fields.Char(
        string='رقم السيارة'
    )
    cube = fields.Float(
        'تكعيب'
    )
    aging_in = fields.Char(
        ' مكان التعتيق'
    )
    transfer_numbers = fields.Float(
        string='عدد النقلات'
    )
    quality_and_quantity = fields.Char(
        string='الجودة والميزان'
    )
    manager = fields.Char(
        string='المشرف'
    )
    under_cube = fields.Float(
        string='تحت التكعيب'
    )

    # def _compute_project_id(self):
    #     for rec in self:
    #         if rec._context.get('active_model') == 'stock.picking':
    #             print("kkkkkkkkkk")
    #             rec.project_id = False
    #             if rec.origin:
    #                 purchase_order_record = self.env['purchase.order'].search([
    #                     ('name', '=', rec.origin)
    #                 ], limit=1)
    #                 if purchase_order_record:
    #                     if purchase_order_record.project_id:
    #                         rec.project_id = purchase_order_record.project_id.id
    #         elif rec._context.get('active_model') == 'project.project':
    #             print("ppppppppppppppppppp")
    #             self.project_id = rec.project_id.id



class StockMove(models.Model):
    _inherit = 'stock.move'
    
    custom_requisition_line_id = fields.Many2one(
        'material.purchase.requisition.line',
        string='Requisitions Line',
        copy=True
    )
