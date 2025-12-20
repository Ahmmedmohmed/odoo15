""" Initialize Project """

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning


class ProjectTask(models.Model):
    _inherit = 'project.task'

    create_request_id = fields.One2many(
        'create.request',
        'project_task_id'
    )
    application_request_id = fields.One2many(
        'application.request',
        'project_task_id'
    )
    equipment_request_id = fields.One2many(
        'equipment.request',
        'project_task_id'
    )
    housing_request_id = fields.One2many(
        'housing.request',
        'project_task_id'
    )
    business_items_id = fields.One2many(
        'business.items',
        'project_task_id'
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
        'project_task_id'
    )
    requisition_ids = fields.Many2many(
        'material.purchase.requisition'
    )

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

    @api.depends('effective_days', 'planned_days')
    def _compute_remaining_days(self):
        for task in self:
            task.remaining_days = task.planned_days - task.effective_days

    @api.constrains('planned_days')
    def check_planned_days(self):
        for rec in self:
            if rec.planned_days < 0:
                raise ValidationError('Initially Planned Days must be positive')

    @api.depends('timesheet_ids.days_spent')
    def _compute_effective_days(self):
        for rec in self:
            if rec.timesheet_ids:
                rec.effective_days = sum(rec.timesheet_ids.mapped('days_spent'))
                print("iffff")
            else:
                rec.effective_days = False
                print("lllllllllllllllllll")

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
                       " 'default_heavy_equipment_id': %s}" % (self.project_id.id, vals, vals_items, vals_fleet)
        }

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

    def action_create_requisition(self):
        requisition_lines_list = []
        if self.create_request_id:
            create_request_lines = self.create_request_id.filtered(lambda x: x.check)
            if create_request_lines:
                for line in create_request_lines:
                    requisition_line = (0, 0, {
                        'requisition_type': 'internal',
                        'product_id': line.product_id.id,
                        'description': line.description,
                        'qty': line.qty,
                        'qty_on_hand': line.qty_on_hand,
                        'uom': line.uom.id
                    })
                    requisition_lines_list.append(requisition_line)
                purchase_requisition = self.env['material.purchase.requisition'].create({
                    'employee_id': self.env.user.employee_id.id,
                    'department_id': self.env.user.employee_id.department_id.id,
                    'company_id': self.env.company.id,
                    'task_id': self.id,
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
                    'view_id': self.env.ref('material_purchase_requisitions.material_purchase_requisition_form_view').id,
                }
            else:
                raise ValidationError('لا يوجد طلبات في حالة تأكيد')
        else:
            raise ValidationError('يجب إنشاء طلب أولاً')
