
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class EmployeeRequest(models.Model):

    _name = "employee.request"
    _rec_name = 'project_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    project_id = fields.Many2one(
        'project.project',
        string='المشروع'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer'
    )
    date = fields.Date()
    company_id = fields.Many2one(
        'res.company'
    )
    user_id = fields.Many2one(
        'res.users',
        string='Project Manager'
    )
    tag_ids = fields.Many2many(
        'project.tags',
        string='Tags'
    )
    application_request_id = fields.One2many(
        'hr.application.request',
        'employee_request_id'
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirmed', 'Confirmed')],
        default='draft',
        tracking=True
    )

    def action_confirm(self):
        for rec in self:
            lines = []
            if rec.application_request_id:
                for line in rec.application_request_id:
                    line = (0, 0, {
                        'job_id': line.job_id.id,
                        'employee_id': line.employee_id.id,
                        'description': line.description,
                        # 'vehicle_type_id': line.vehicle_type_id.id,
                        # 'fleet_id': line.fleet_id.id,
                        'qty': line.qty,
                        'tag_ids': line.tag_ids.ids,
                        'note': line.note,
                        # 'supplier_id': line.supplier_id.id,
                    })
                    lines.append(line)
                hr_work_request = self.env['hr.work.request'].create({
                    # 'vehicle_request_id': rec.id,
                    'project_id': rec.project_id.id,
                    'partner_id': rec.partner_id.id,
                    'date': rec.date,
                    'company_id': rec.company_id.id,
                    'user_id': rec.user_id.id,
                    'tag_ids': rec.tag_ids.ids,
                    'hr_work_request_lines': lines,
                })
                rec.state = 'confirmed'
            else:
                raise ValidationError(_('يجب إنشاء طلب تعيين موظفين أولاً !'))


class HrApplicationRequest(models.Model):
    _name = 'hr.application.request'

    job_id = fields.Many2one(
        'hr.job',
        string='مسمي الوظيفة',
        required=True,
    )
    description = fields.Char(
        string='موقف الوظيفة(استكال هيكل/مؤقت/مستحدث)',
    )
    qty = fields.Float(
        string='العدد المطلوب',
        required=True,
    )
    tag_ids = fields.Many2many(
        comodel_name="project.tags",
        string="العلامات"
    )
    note = fields.Char(
        string="ملاحظات"
    )
    employee_request_id = fields.Many2one(
        'employee.request',
    )
    project_task_id = fields.Many2one(
        'project.task',
        string='Task',
    )
    employee_id = fields.Many2one(comodel_name="hr.employee",
                                  string="الموظف")

    subsistence = fields.Float(
        string='إعاشة ',
        # related="projecsubsistence"
    )
    # nature_substitute = fields.Float(
    #     string='بدل ط ع ',
    #     # related="project_id.nature_substitute"

    # )
    quantity = fields.Float(
        string='الكمية  ',
    )

    # @api.constrains('fleet_id')
    # # def _check_fleet_id(self):
    # #     for rec in self:
    # #         open_request = self.env['work.request'].search([
    # #             ('state', '=', 'open')
    # #         ])
    # #         if open_request:
    # #             open_fleet = open_request.work_request_lines.mapped('fleet_id')
    # #             if rec.fleet_id in open_fleet and open_request.work_request_lines.closed == False:
    # #                 raise ValidationError(_('هذه المعدة موجوده في أمر شغل مفتوح حالياً !'))
    # #

    @api.constrains('employee_id')
    def _check_employee_id(self):
        for rec in self:
            open_requests = self.env['hr.work.request'].search([
                ('state', '=', 'open')
            ])
            for request in open_requests:
                open_employee = request.hr_work_request_lines.mapped('employee_id')
                if rec.employee_id in open_employee and any(not line.closed for line in request.hr_work_request_lines):
                    raise ValidationError(_('هذا الموظف موجود في أمر شغل موظفين مفتوح حالياً !'))
