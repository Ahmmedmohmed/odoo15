from odoo import models, fields, api, _


class AppraisalAppraisal(models.Model):
    _name = 'appraisal.appraisal'
    _rec_name = 'employee_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee")

    # هذا الحقل "مراية" لراتب الموظف، هيتحدث لوحده لما نحدث الموظف في آخر خطوة
    appraisal_wage = fields.Float(
        string='Actual wage',
        related='employee_id.actual_wage',
        store=True,
        readonly=True
    )

    employee_barcode = fields.Char(string="Employee ID", required=False, )
    title = fields.Char(string="Title", required=False, )
    hiring_date = fields.Date(string="Hiring Date", required=False, )
    department_id = fields.Many2one(comodel_name="hr.department", string="Department", required=False, )
    manager_id = fields.Many2one(comodel_name="hr.employee", string="Manager / Supervisor Name", required=False, )
    last_performance_date = fields.Date(string="Last Performance Date", )
    appraisal_date = fields.Date(string="Appraisal Submission Date", )
    notes = fields.Text(string="Comments", required=False, )
    rating_scale_ids = fields.One2many(comodel_name="rate.scale.line", inverse_name="appraisal_line_id", )
    hr_rating_scale_ids = fields.One2many(comodel_name="rate.scale.line", inverse_name="hr_appraisal_id", )

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)

    trainings_courses_ids = fields.One2many(comodel_name="trainings.courses", inverse_name="appraisal_id", string="", )

    # -----------------------------------------------------------
    # 1. تعديل حقل الحالة ليشمل الـ 3 مراحل
    # -----------------------------------------------------------
    state = fields.Selection(string="Status", selection=[
        ('draft', 'Draft'),
        ('manager_approve', 'Manager Approval'),  # انتظار موافقة HR
        ('hr_approve', 'HR Approval'),  # انتظار موافقة CEO
        ('done', 'CEO Approved'),  # تم الانتهاء وتحديث الراتب
    ], default='draft', tracking=True)
    # -----------------------------------------------------------

    total_performance = fields.Char(string="Total Performance", compute='calculate_total_performance', )
    total_performance_percentage = fields.Float(
        string="Total Performance",
        compute='calculate_total_performance_percentage',
        store=False
    )
    hr_total_performance = fields.Char(string="Hr Total Performance", compute='calculate_hr_total_performance', )

    employee_wage = fields.Float(string="Wage", required=False, )
    is_need_course = fields.Boolean(string="Need Courses", )
    estimate_salary = fields.Float(string="Estimate Salary")

    rank = fields.Char(
        string="Rank",
        compute='_compute_rank',
        store=True,
        readonly=False,
        tracking=True
    )

    @api.depends('employee_id.employee_rank')
    def _compute_rank(self):
        for rec in self:
            if rec.employee_id.employee_rank:
                rec.rank = rec.employee_id.employee_rank
            elif not rec.rank:
                rec.rank = False

    # ... (دوال الحسابات كما هي بدون تغيير) ...
    @api.depends('hr_rating_scale_ids')
    def calculate_hr_total_performance(self):
        # ... (نفس الكود القديم) ...
        self.hr_total_performance = ''
        for rec in self:
            total0 = 0
            total1 = 0
            total2 = 0
            total3 = 0
            total4 = 0
            total5 = 0
            performance_total = []
            if rec.hr_rating_scale_ids:
                for line in rec.hr_rating_scale_ids:
                    if line.evaluation == False:
                        total0 += 1
                    if line.evaluation == '1':
                        total1 += 1
                    if line.evaluation == '2':
                        total2 += 1
                    if line.evaluation == '3':
                        total3 += 1
                    if line.evaluation == '4':
                        total4 += 1
                    if line.evaluation == '5':
                        total5 += 1
            performance_total.append(total0)
            performance_total.append(total1)
            performance_total.append(total2)
            performance_total.append(total3)
            performance_total.append(total4)
            performance_total.append(total5)
            if total1 == total2 == total3 == total4 == total5:
                rec.hr_total_performance = ''
            else:
                if max(performance_total) == total1:
                    rec.hr_total_performance = 'Unsatisfactory'
                if max(performance_total) == total2:
                    rec.hr_total_performance = 'Needs Improvement'
                if max(performance_total) == total3:
                    rec.hr_total_performance = 'Meets Expectations'
                if max(performance_total) == total4:
                    rec.hr_total_performance = 'Exceeds Expectations'
                if max(performance_total) == total5:
                    rec.hr_total_performance = 'Exceptional'

    @api.depends('rating_scale_ids')
    def calculate_total_performance_percentage(self):
        # ... (نفس الكود القديم) ...
        for rec in self:
            rec.total_performance_percentage = False
            if rec.rating_scale_ids:
                total_lines = len(rec.rating_scale_ids) * 5
                total_values = 0
                for line in rec.rating_scale_ids:
                    if line.evaluation == '1':
                        total_values += 1
                    if line.evaluation == '2':
                        total_values += 2
                    if line.evaluation == '3':
                        total_values += 3
                    if line.evaluation == '4':
                        total_values += 4
                    if line.evaluation == '5':
                        total_values += 5
                if total_lines > 0:
                    rec.total_performance_percentage = total_values / total_lines

    @api.depends('rating_scale_ids')
    def calculate_total_performance(self):
        # ... (نفس الكود القديم) ...
        self.total_performance = ''
        for rec in self:
            total1 = 0
            total2 = 0
            total3 = 0
            total4 = 0
            total5 = 0
            performance_total = []
            if rec.rating_scale_ids:
                for line in rec.rating_scale_ids:
                    if line.evaluation == '1':
                        total1 += 1
                    if line.evaluation == '2':
                        total2 += 1
                    if line.evaluation == '3':
                        total3 += 1
                    if line.evaluation == '4':
                        total4 += 1
                    if line.evaluation == '5':
                        total5 += 1
            performance_total.append(total1)
            performance_total.append(total2)
            performance_total.append(total3)
            performance_total.append(total4)
            performance_total.append(total5)
            if total1 == total2 == total3 == total4 == total5:
                rec.hr_total_performance = ''

            else:
                if max(performance_total) == total1:
                    rec.total_performance = 'Unsatisfactory'
                if max(performance_total) == total2:
                    rec.total_performance = 'Needs Improvement'
                if max(performance_total) == total3:
                    rec.total_performance = 'Meets Expectations'
                if max(performance_total) == total4:
                    rec.total_performance = 'Exceeds Expectations'
                if max(performance_total) == total5:
                    rec.total_performance = 'Exceptional'

    @api.onchange('employee_id')
    def manager_filter_employee(self):
        # ... (نفس الكود القديم) ...
        user = self.env.user
        lines = []
        if user.has_group('nile_air_appraisal.group_hr_manager_employee') or user.has_group('base.group_system'):
            lines = self.env['hr.employee'].search([]).ids
        else:
            direct_subordinates = self.env['hr.employee'].search([('parent_id.user_id', '=', user.id)])
            lines.extend(direct_subordinates.ids)
            dept_subordinates = self.env['hr.employee'].search([('department_id.manager_id.user_id', '=', user.id)])
            lines.extend(dept_subordinates.ids)
            myself = self.env['hr.employee'].search([('user_id', '=', user.id)])
            lines.extend(myself.ids)
        lines = list(set(lines))
        return {
            'domain': {'employee_id': [('id', 'in', lines)]}
        }

    @api.onchange('employee_id')
    def get_employee_last_data(self):
        # ... (نفس الكود القديم، فقط تأكدت أن الحالة النهائية هي done)
        if not self.employee_id:
            self.employee_barcode = False
            self.rank = False
            self.hiring_date = False
            self.title = False
            self.department_id = False
            self.manager_id = False
            self.employee_wage = 0.0
            self.estimate_salary = 0.0
            self.is_need_course = False
            self.notes = False
            self.last_performance_date = False
            return
        self.employee_barcode = self.employee_id.barcode
        self.rank = getattr(self.employee_id, 'employee_rank', False)
        self.hiring_date = self.employee_id.first_contract_date or self.employee_id.create_date.date()

        # بحثنا عن done بدلاً من confirm
        last_appraisal = self.search([
            ('id', '!=', self._origin.id),
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'done')
        ], order='id desc', limit=1)

        if last_appraisal:
            self.last_performance_date = last_appraisal.appraisal_date
            self.title = last_appraisal.title
            self.department_id = last_appraisal.department_id
            self.manager_id = last_appraisal.manager_id
            self.employee_wage = last_appraisal.employee_wage
            self.estimate_salary = last_appraisal.estimate_salary
            self.is_need_course = last_appraisal.is_need_course
            self.notes = last_appraisal.notes
            self.hr_total_performance = last_appraisal.hr_total_performance
        else:
            self.last_performance_date = False
            self.title = False
            self.department_id = False
            self.manager_id = False
            self.employee_wage = 0.0
            self.estimate_salary = 0.0
            self.is_need_course = False
            self.notes = False

    def get_questions(self):
        lines = [(5, 0, 0)]
        for rec in self.env['rate.scale'].search([('is_hr_question', '=', False)]):
            lines.append((0, 0, {
                'questions': rec.questions
            }))
        self.update({'rating_scale_ids': lines})

    def hr_get_questions(self):
        lines = [(5, 0, 0)]
        for rec in self.env['rate.scale'].search([('is_hr_question', '=', True)]):
            lines.append((0, 0, {
                'questions': rec.questions
            }))
        self.update({'hr_rating_scale_ids': lines})

    # -----------------------------------------------------------
    # 2. دوال الزراير الجديدة (Workflow)
    # -----------------------------------------------------------

    # مرحلة 1: موافقة المدير المباشر
    def action_manager_confirm(self):
        for rec in self:
            rec.state = 'manager_approve'

    # مرحلة 2: موافقة الـ HR
    def action_hr_confirm(self):
        for rec in self:
            rec.state = 'hr_approve'

    # مرحلة 3: موافقة الـ CEO (التحديث الفعلي للراتب)
    def action_ceo_confirm(self):
        for rec in self:
            # تحديث راتب الموظف في موديل الموظفين
            if rec.estimate_salary > 0:
                rec.employee_id.sudo().write({
                    'actual_wage': rec.estimate_salary
                })
            rec.state = 'done'

    def set_to_draft(self):
        self.state = 'draft'

    # تحديث دالة الأكشن سيرفر لتنفيذ أول خطوة
    def confirm_multi_appraisal(self):
        for rec in self:
            if rec.state == 'draft':
                rec.action_manager_confirm()

class RateScale(models.Model):
    _name = 'rate.scale'


    questions = fields.Text(string="Questions", required=False, )
    is_hr_question = fields.Boolean(string="IS HR Question",  )
    appraisal_id = fields.Many2one(comodel_name="appraisal.appraisal",)
class RateScaleScale(models.Model):
    _name = 'rate.scale.line'


    questions = fields.Text(string="Questions", required=False, )
    evaluation = fields.Selection(string="Evaluation", selection=[('0','0'),('1', '1'), ('2', '2'),('3', '3'), ('4', '4'),('5', '5'), ], required=False, )
    appraisal_line_id = fields.Many2one(comodel_name="appraisal.appraisal", string="", required=False, )
    hr_appraisal_id = fields.Many2one(comodel_name="appraisal.appraisal",)





class TrainingsCourses(models.Model):
    _name = 'trainings.courses'

    courses_id = fields.Many2one(comodel_name="courses.screen", string="Course Name", required=True, )
    suggested_provider = fields.Char(string="Suggested Provider", required=False, )
    estimated_cost = fields.Float(string="Estimated Cost", required=False, )
    date = fields.Date(string="Preferred Date/Quarter", required=False, )
    appraisal_id = fields.Many2one(comodel_name="appraisal.appraisal", string="", required=False, )
