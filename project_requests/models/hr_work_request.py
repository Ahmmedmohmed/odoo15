
from odoo import fields, models, api, _


class HrWorkRequest(models.Model):

    _name = "hr.work.request"
    # _rec_name = 'vehicle_request_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_request_id = fields.Many2one(
        'employee.request'
    )
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
    hr_work_request_lines = fields.One2many(
        'hr.work.request.line',
        'hr_work_request_id'
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Open'),
         ('closed', 'Closed')],
        default='draft',
        tracking=True
    )

    open_date = fields.Datetime(
        readonly=True
    )
    close_date = fields.Datetime(
        readonly=True
    )
    duration = fields.Float(
        string="Duration (Hours)",
        compute='_compute_duration',
        store=True,
        # digits=(12, 6)
    )

    def action_open(self):
        for rec in self:
            rec.state = 'open'
            rec.open_date = fields.datetime.now()
            if rec.user_id:
                activity_vals = {
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'summary': 'Employee Work Request opened',
                    'note': 'This Employee work request is Opined ',
                    'date_deadline': fields.Date.today(),
                    'res_id': rec.id,
                    'res_model_id': self.env.ref('project_requests.model_hr_work_request').id,
                    'user_id': rec.user_id.id,
                }
                self.env['mail.activity'].create(activity_vals)
        project = self.env['project.project'].search([('id', '=', self.project_id.id)])
        print("project_follow  ", project)
        if project:
            # project_follow.date = fields.Date.today()

            employee_lines = []
            for line in self.hr_work_request_lines:
                employee_lines.append((0, 0, {
                    'employee_id': line.employee_id.id,
                    'job_id': line.job_id.id,
                    # 'vehicle_type_id': line.vehicle_type_id.id,
                    'qty': line.qty,
                    'note': line.note,
                    # 'from_request_work': True,
                }))
                line.opened = True
            project.write({
                'application_request_id': employee_lines
            })

    def action_close(self):
        for rec in self:
            rec.state = 'closed'
            rec.close_date = fields.datetime.now()
            if rec.user_id:
                activity_vals = {
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'summary': 'Employee Work Request closed',
                    'note': 'This Employee work request is closed ',
                    'date_deadline': fields.Date.today(),
                    'res_id': rec.id,
                    'res_model_id': self.env.ref('project_requests.model_hr_work_request').id,
                    'user_id': rec.user_id.id,
                }
                self.env['mail.activity'].create(activity_vals)

    #
    @api.depends('open_date', 'close_date', 'state')
    def _compute_duration(self):
        for rec in self:
            if rec.open_date and rec.close_date and rec.state == 'closed':
                delta = rec.close_date - rec.open_date
                # Calculate total hours including fractional hours
                rec.duration = delta.total_seconds() / 3600
            else:
                rec.duration = 0.0




class HrWorkRequestLine(models.Model):

    _name = "hr.work.request.line"

    hr_work_request_id = fields.Many2one(
        'hr.work.request'
    )
    description = fields.Char(
        # required=True
    )
    job_id = fields.Many2one(
        'hr.job',
        string='مسمي الوظيفة',
        required=True,
    )

    # vehicle_type_id = fields.Many2one(
    #     'vehicle.type'
    # )
    # fleet_id = fields.Many2one(
    #     'fleet.vehicle',
    #     string='نوع المعدة'
    # )
    employee_id = fields.Many2one(
        'hr.employee',
        string='الموظف',
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
    supplier_id = fields.Many2one(
        'res.partner',
        string='المورد'
    )

    closed = fields.Boolean(string="Close")
    opened = fields.Boolean(string="Opened")

    def action_open_from_lines(self):
        project = self.env['project.project'].search([('id', '=', self.hr_work_request_id.project_id.id)])
        print("project_follow  ", project)
        if project:
            # project_follow.date = fields.Date.today()

            employee_lines = []
            for line in self:
                employee_lines.append((0, 0, {
                    'employee_id': line.employee_id.id,
                    # 'supplier_id': line.supplier_id.id,
                    'job_id': line.job_id.id,
                    'qty': line.qty,
                    'note': line.note,
                    # 'from_request_work': True,
                }))
                line.opened = True
            project.write({
                'application_request_id': employee_lines
            })
