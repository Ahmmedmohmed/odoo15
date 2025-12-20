# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectProject(models.Model):
    _inherit = 'project.project'

    warehouse_id = fields.Many2one("stock.warehouse",required=True)



    def action_open_custom_receipts(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'خارجي',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'views': [
                (self.env.ref('invintory_delevery_recept_control.stock_picking_recept_tree_view').id, 'tree'),
                (False, 'form'),  # use default form view
            ],
            'domain': [('picking_type_code', '=', 'incoming'),
                       ('project_id', '=', self.id),
                       # ('billed_picking', '=', False)
                       ],
            'context': {'default_project_id': self.id,
                        'default_picking_type_code': 'incoming',
                        'default_picking_type_id': self.warehouse_id.in_type_id.id,

                        },
            'target': 'current',
        }

    def action_open_custom_delivery(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'داخلي',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'views': [
                (self.env.ref('invintory_delevery_recept_control.stock_picking_delivery_tree_view').id, 'tree'),
                (False, 'form'),  # use default form view
            ],
             'domain': [
            ('picking_type_code', '=', 'outgoing'),
                 ('project_id', '=', self.id),
                 # ('billed_picking', '=', False)
        ],
        'context': {
            'default_project_id': self.id,
            'default_picking_type_code': 'outgoing',
            'default_picking_type_id': self.warehouse_id.out_type_id.id,
        },
            'target': 'current',

        }


    def action_open_custom_fleet_equipment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'المعدات',
            'res_model': 'fleet.equipment',
            'view_mode': 'tree,form',
            # 'views': [
            #     (self.env.ref('invintory_delevery_recept_control.fleet_vehicle_smart_button_tree_view').id, 'tree'),
            #     (False, 'form'),  # use default form view
            # ],
        #      'domain': [
        #          ('billed_equipment', '=', False)
        # ],
            'target': 'current',

        }

    def action_open_custom_car(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'السيارات',
            'res_model': 'car.car',
            'view_mode': 'tree,form',

            # 'domain': [
            #     '|',('record_bill_state', '=', 'not_billed'),('record_bill_state', '=', False)
            # ],
            'target': 'current',

        }

    def action_open_all_bills(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'الفواتير',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'target': 'current',


            'context': {
                'default_move_type': 'out_invoice',
            }


        }

    def action_open_project_employee(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'الحضور',
            'res_model': 'hr.attendance',
            'view_mode': 'tree',
            'target': 'current',

                 'domain': [
                     ('project_id', '=', self.id)
            ],

        }

