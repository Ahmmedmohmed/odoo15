""" Initialize Project """

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.tools.populate import compute


class ProjectProject(models.Model):
    _inherit = 'project.project'

    create_request_id = fields.One2many(
        'create.request',
        'project_id'
    )
    application_request_id = fields.One2many(
        'application.request',
        'project_id'
    )
    equipment_request_id = fields.One2many(
        'equipment.request',
        'project_id'
    )
    housing_request_id = fields.One2many(
        'housing.request',
        'project_id'
    )
    business_items_id = fields.One2many(
        'business.items',
        'project_id'
    )
    planned_days = fields.Integer(
        "Initially Planned Days",
        tracking=True
    )
    timesheet_progress = fields.Float(
        "Progress",
        compute='_compute_timesheet_progress',
        store=True,
        group_operator="avg"
    )
    effective_days = fields.Integer(
        "Days Spent",
        compute='_compute_effective_days',
        compute_sudo=True,
        store=True
    )
    remaining_days = fields.Integer(
        "Remaining Days",
        compute='_compute_remaining_days',
        store=True,
        readonly=True
    )
    timesheet_id = fields.One2many(
        'account.analytic.line',
        'project_id'
    )
    requisition_ids = fields.Many2many(
        'material.purchase.requisition'
    )
    project_follow_ids = fields.Many2many(
        'project.follow',
        compute='compute_project_follow_ids'
    )



    subsistence = fields.Float(
        string='إعاشة ',
    )
    # nature_substitute = fields.Float(
    #     string='بدل ط ع ',
    # )


    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ], string="Status", default="draft")


    def action_create_lines_in_fleet(self):
        for rec in self:
            if not rec.equipment_request_id:
                raise UserError('يجب إنشاء طلب معدة أولا')
            lines = []
            for line in rec.equipment_request_id:
                lines.append((0, 0, {
                    # 'description': line.description,
                    'vehicle_type_id': line.vehicle_type_id.id,
                    'fleet_id': line.fleet_id.id,
                    'fleet_model_id': line.fleet_model_id.id,
                    'qty': line.qty,
                    'tag_ids': line.tag_ids.ids,
                    'note': line.note,
                    'supplier_id': line.supplier_id.id,
                }))
            request_record = self.env['vehicle.request'].create({
                'state': 'draft',
                'project_id': rec.id,
                'partner_id': rec.partner_id.id,
                'date': fields.Date.today(),
                'company_id': rec.company_id.id,
                'user_id': rec.user_id.id,
                'tag_ids': rec.tag_ids.ids,
                'vehicle_request_lines': lines,
            })

    def action_create_lines_in_employee_request(self):
        for rec in self:
            if not rec.application_request_id:
                raise UserError('يجب إنشاء طلب تعيين أولا')
            lines = []
            for line in rec.application_request_id:
                lines.append((0, 0, {
                    # 'description': line.description,
                    # 'vehicle_type_id': line.vehicle_type_id.id,
                    'job_id': line.job_id.id,
                    # 'fleet_model_id': line.fleet_model_id.id,
                    'qty': line.qty,
                    'tag_ids': line.tag_ids.ids,
                    'note': line.note,
                    # 'supplier_id': line.supplier_id.id,
                }))
            request_record = self.env['employee.request'].create({
                'state': 'draft',
                'project_id': rec.id,
                'partner_id': rec.partner_id.id,
                'date': fields.Date.today(),
                'company_id': rec.company_id.id,
                'user_id': rec.user_id.id,
                'tag_ids': rec.tag_ids.ids,
                'application_request_id': lines,
            })

    def action_view_vehicle_requests(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'المعدات',
            'res_model': 'vehicle.request',
            'view_mode': 'tree,form',
            # 'views': [
            #     (self.env.ref('invintory_delevery_recept_control.fleet_vehicle_smart_button_tree_view').id, 'tree'),
            #     (False, 'form'),  # use default form view
            # # ],
            # 'domain': [
            #     ('billed_vehicle', '=', False)
            # ],
            'target': 'current',

        }

    @api.constrains('planned_days')
    def check_planned_days(self):
        for rec in self:
            if rec.planned_days < 0:
                raise ValidationError('Initially Planned Days must be positive')

    @api.depends('effective_days', 'planned_days')
    def _compute_remaining_days(self):
        for task in self:
            task.remaining_days = task.planned_days - task.effective_days

    @api.depends('timesheet_id.days_spent')
    def _compute_effective_days(self):
        for rec in self:
            if rec.timesheet_id:
                rec.effective_days = sum(rec.timesheet_id.mapped('days_spent'))
            else:
                rec.effective_days = False

    @api.depends('effective_days', 'planned_days')
    def _compute_timesheet_progress(self):
        for task in self:
            if task.planned_days > 0:
                if task.effective_days > task.planned_days:
                    task.timesheet_progress = 100
                else:
                    task.timesheet_progress = round(100.0 * task.effective_days / task.planned_days, 2)
            else:
                task.timesheet_progress = 0.0

    def compute_project_follow_ids(self):
        project_follow_records = self.env['project.follow'].search([
            ('project_id', '=', self.id)
        ])
        if project_follow_records:
            self.project_follow_ids = project_follow_records.ids
        else:
            self.project_follow_ids = False

    def action_show_delivery(self):
        for rec in self:
            domain = []
            purchase_records = self.env['purchase.order'].search([
                ('project_id', '=', rec.id)
            ])
            if purchase_records:
                for purchase in purchase_records:
                    related_stock_picking = self.env['stock.picking'].search([
                        ('origin', '=', purchase.name)
                    ])
                    if related_stock_picking:
                        domain.append(related_stock_picking.id)
            view_tree = {
                'name': 'Delivery',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'stock.picking',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', domain)],
            }
            return view_tree

    def action_show_requisition(self):
        for rec in self:
            domain = [('id', 'in', rec.requisition_ids.ids)]
            view_tree = {
                'name': 'Requisitions',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'material.purchase.requisition',
                'type': 'ir.actions.act_window',
                'domain': domain,
            }
            return view_tree

    def action_show_reports(self):
        for rec in self:
            domain = [('id', 'in', rec.project_follow_ids.ids)]
            view_tree = {
                'name': 'متابعة المشروع',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'project.follow',
                'type': 'ir.actions.act_window',
                'domain': domain,
            }
            return view_tree

    def action_create_report(self):
        if not self.create_request_id:
            raise ValidationError(_('يجب إنشاء طلب مشتريات خامات أولاً'))
        context = dict(self.env.context)
        context.update({'project_id': self.id})
        vals = []
        for request_line in self.create_request_id:
            vals.append((0, 0, {'product_id': request_line.product_id.id,
                                'basic_quantity': request_line.qty}))
        vals_items = []
        for item_line in self.business_items_id:
            vals_items.append((0, 0, {'product_id': item_line.product_id.id,
                                      'uom': item_line.uom.id,
                                      'basic_quantity': item_line.qty}))
        vals_fleet = []
        for fleet_line in self.equipment_request_id:
            vals_fleet.append((0, 0, {'fleet_id': fleet_line.fleet_id.id,
                                      'partner_id': fleet_line.supplier_id.id}))
        return {
            'name': _('متابعة المشروع'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'current',
            'res_model': 'project.follow',
            'view_id': self.env.ref('project_requests.project_follow_form').id,
            'context': "{'default_project_id': %s, 'default_daily_supplies_id': %s, 'default_executed_works_id': %s,"
                       " 'default_heavy_equipment_id': %s}" % (self.id, vals, vals_items, vals_fleet)
        }

    #
    # def action_create_report(self):
    #     if not self.create_request_id:
    #         raise ValidationError(_('يجب إنشاء طلب مشتريات خامات أولاً'))
    #     context = dict(self.env.context)
    #     context.update({'project_id': self.id})
    #     vals = []
    #     for request_line in self.create_request_id:
    #         vals.append((0, 0, {'product_id': request_line.product_id.id,
    #                             'basic_quantity': request_line.qty}))
    #     vals_items = []
    #     for item_line in self.business_items_id:
    #         vals_items.append((0, 0, {'product_id': item_line.product_id.id,
    #                                   'uom': item_line.uom.id,
    #                                   'basic_quantity': item_line.qty}))
    #     vals_fleet = []
    #     for fleet_line in self.equipment_request_id:
    #         vals_fleet.append((0, 0, {'fleet_id': fleet_line.fleet_id.id,
    #                                   'partner_id': fleet_line.supplier_id.id}))
    #     return {
    #         'name': _('متابعة المشروع'),
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'target': 'current',
    #         'res_model': 'project.follow',
    #         'view_id': self.env.ref('project_requests.project_follow_form').id,
    #         'context': "{'default_project_id': %s, 'default_daily_supplies_id': %s, 'default_executed_works_id': %s,"
    #                    " 'default_heavy_equipment_id': %s}" % (self.id, vals, vals_items, vals_fleet)
    #     }

    # def action_create_report(self):
    #     project_follow = self.env['project.follow'].search([('project_id', '=', self.id)])
    #     if not project_follow:
    #         if not self.create_request_id:
    #             raise ValidationError(_('يجب إنشاء طلب مشتريات خامات أولاً'))
    #         context = dict(self.env.context)
    #         context.update({'project_id': self.id})
    #         vals = []
    #         for request_line in self.create_request_id:
    #             vals.append((0, 0, {'product_id': request_line.product_id.id,
    #                                 'basic_quantity': request_line.qty}))
    #         vals_items = []
    #         for item_line in self.business_items_id:
    #             vals_items.append((0, 0, {'product_id': item_line.product_id.id,
    #                                       'uom': item_line.uom.id,
    #                                       'basic_quantity': item_line.qty}))
    #         vals_fleet = []
    #         for fleet_line in self.equipment_request_id:
    #             vals_fleet.append((0, 0, {'fleet_id': fleet_line.fleet_id.id,
    #                                       'partner_id': fleet_line.supplier_id.id}))
    #
    #         return {
    #             'name': _('متابعة المشروع'),
    #             'type': 'ir.actions.act_window',
    #             'view_mode': 'form',
    #             'target': 'current',
    #             'res_model': 'project.follow',
    #             'view_id': self.env.ref('project_requests.project_follow_form').id,
    #             'context': "{'default_project_id': %s, 'default_daily_supplies_id': %s, 'default_executed_works_id': %s,"
    #                        " 'default_heavy_equipment_id': %s}" % (self.id, vals, vals_items, vals_fleet)
    #         }
    #
    #     else:
    #         return {
    #             'name': _('متابعة المشروع'),
    #             'type': 'ir.actions.act_window',
    #             'view_mode': 'form',
    #             'target': 'current',
    #             'res_model': 'project.follow',
    #             'view_id': self.env.ref('project_requests.project_follow_form').id,
    #             'res_id': project_follow.id,
    #             'context': {'create': False,}
    #
    #         }

    def action_create_requisition(self):
        requisition_lines_list = []
        if self.create_request_id:
            create_request_lines = self.create_request_id.filtered(lambda x: x.check)
            if create_request_lines:
                for line in create_request_lines:
                    requisition_line = (0, 0, {
                        'requisition_type': 'purchase',
                        'product_id': line.product_id.id,
                        'description': line.description,
                        'qty': line.qty,
                        'qty_on_hand': line.qty_on_hand,
                        'uom': line.uom.id,
                    })
                    requisition_lines_list.append(requisition_line)
                purchase_requisition = self.env['material.purchase.requisition'].create({
                    'employee_id': self.env.user.employee_id.id,
                    'department_id': self.env.user.employee_id.department_id.id,
                    'company_id': self.env.company.id,
                    'project_id': self.id,
                    'request_date': fields.Date.today(),
                    'requisition_line_ids': requisition_lines_list
                })
                self.requisition_ids += purchase_requisition
                return {
                    'name': _('Purchase Requisitions'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'target': 'current',
                    'res_model': 'material.purchase.requisition',
                    'res_id': purchase_requisition.id,
                    'view_id': self.env.ref(
                        'material_purchase_requisitions.material_purchase_requisition_form_view').id,
                }
            else:
                raise ValidationError('لا يوجد طلبات في حالة تأكيد')
        else:
            raise ValidationError('يجب إنشاء طلب أولاً')
