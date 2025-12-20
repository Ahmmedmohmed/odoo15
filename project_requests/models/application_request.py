from odoo import fields, api, models


class ApplicationRequest(models.Model):
    _name = 'application.request'

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
    project_id = fields.Many2one(
        'project.project',
        string='Project',
    )
    project_task_id = fields.Many2one(
        'project.task',
        string='Task',
    )
    employee_id = fields.Many2one(comodel_name="hr.employee",
                                  string="الموظف",
    domain = "[('job_id','=',job_id)]"
    )

    daily_amount = fields.Float(compute="_compute_daily_amount",
                                store=True,

      )


    subsistence = fields.Float(
        string='إعاشة ',
        related="project_id.subsistence"
    )
    nature_substitute = fields.Float(
        string='بدل ط ع ',
        # related="project_id.nature_substitute"

    )
    quantity = fields.Float(
        string='العدد  ',
    )
    subsistence_quantity = fields.Integer(
        string='عدد الاعاشة  ',
    )

    date_from = fields.Date()
    date_to = fields.Date()

    nature_substitute_total = fields.Float(
        compute="_compute_employee_totals",
    )
    subsistence_total = fields.Float(
        compute="_compute_employee_totals"
    )

    @api.depends('employee_id')
    def _compute_daily_amount(self):
        for rec in self:
            daily_amount = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')])
            print("ddddd",daily_amount)

            rec.daily_amount = daily_amount.daily_amount


    @api.depends('subsistence', 'nature_substitute', 'quantity', 'subsistence_quantity', 'daily_amount')
    def _compute_employee_totals(self):
        for rec in self:
            if rec.nature_substitute or rec.subsistence:
                if rec.nature_substitute:
                    rec.nature_substitute_total = (rec.quantity * rec.daily_amount) * rec.nature_substitute
                    rec.subsistence_total = rec.subsistence_total  # Must set this too!
                if rec.subsistence:
                    rec.subsistence_total = rec.subsistence_quantity * rec.subsistence
                    rec.nature_substitute_total = rec.nature_substitute_total  # Must set this too!
            else:
                rec.nature_substitute_total = rec.nature_substitute_total
                rec.subsistence_total = rec.subsistence_total
