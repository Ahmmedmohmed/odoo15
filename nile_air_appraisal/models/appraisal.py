from odoo import models, fields, api
class AppraisalAppraisal(models.Model):
    _name = 'appraisal.appraisal'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee")
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
    last_performance_date = fields.Date(string="Last Performance Date",)
    appraisal_date = fields.Date(string="Appraisal Submission Date",)
    notes = fields.Text(string="Comments", required=False, )
    rating_scale_ids = fields.One2many(comodel_name="rate.scale.line",inverse_name="appraisal_line_id",)
    hr_rating_scale_ids = fields.One2many(comodel_name="rate.scale.line",inverse_name="hr_appraisal_id",)

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)

    trainings_courses_ids = fields.One2many(comodel_name="trainings.courses", inverse_name="appraisal_id", string="",)
    state = fields.Selection(string="", selection=[('draft', 'Draft'), ('confirm', 'Confirm'), ],default='draft' )
    total_performance = fields.Char(string="Total Performance",compute='calculate_total_performance',)
    total_performance_percentage = fields.Char(string="Total Performance",compute='calculate_total_performance_percentage',)
    hr_total_performance = fields.Char(string="Hr Total Performance",compute='calculate_hr_total_performance',)

    employee_wage = fields.Float(string="Wage",  required=False, )
    is_need_course = fields.Boolean(string="Need Courses",  )
    rank = fields.Char()
    estimate_salary = fields.Float()


    @api.onchange('employee_id')
    def get_last_performance_date(self):
        appraisal_record=self.search([('id','!=',self._origin.id),('employee_id','=',self.employee_id.id),
                                      ('state','=','confirm')],order='id desc',limit=1)
        if appraisal_record:
            self.last_performance_date=appraisal_record.appraisal_date

    @api.depends('hr_rating_scale_ids')
    def calculate_hr_total_performance(self):
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
            if total1==total2==total3==total4==total5:
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
        self.total_performance=''
        for rec in self:
            total1=0
            total2=0
            total3=0
            total4=0
            total5=0
            performance_total=[]
            if rec.rating_scale_ids:
                for line in rec.rating_scale_ids:
                    if line.evaluation=='1':
                        total1+=1
                    if line.evaluation=='2':
                        total2 += 1
                    if line.evaluation=='3':
                        total3 += 1
                    if line.evaluation=='4':
                        total4 += 1
                    if line.evaluation=='5':
                        total5 += 1
            performance_total.append(total1)
            performance_total.append(total2)
            performance_total.append(total3)
            performance_total.append(total4)
            performance_total.append(total5)
            if total1==total2==total3==total4==total5:
                rec.hr_total_performance = ''

            else:
                if max(performance_total)==total1:
                    rec.total_performance='Unsatisfactory'
                if max(performance_total)==total2:
                    rec.total_performance='Needs Improvement'
                if max(performance_total)==total3:
                    rec.total_performance='Meets Expectations'
                if max(performance_total)==total4:
                    rec.total_performance='Exceeds Expectations'
                if max(performance_total)==total5:
                    rec.total_performance='Exceptional'


    @api.onchange('employee_id')
    def manager_filter_employee(self):
        lines=[]
        employee_record=self.env['hr.employee'].search([])
        for empl in employee_record:
            if self.env.user.id==empl.parent_id.user_id.id:
                lines.append(empl.id)
            if self.env.user.has_group('nile_air_appraisal.group_hr_manager_employee'):
                lines.append(empl.id)

        return {
            'domain': {'employee_id': [('id', 'in', lines)]}
        }

    def button_confirm(self):
        self.state='confirm'
    def set_to_draft(self):
        self.state='draft'


    @api.onchange('employee_id')
    def calculate_employee_data(self):
        self.employee_barcode=self.employee_id.barcode
        self.title=self.employee_id.job_title
        self.department_id=self.employee_id.department_id.id
        self.manager_id=self.employee_id.parent_id.id
        contract_record=self.env['hr.contract'].search([('employee_id','=',self.employee_id.id)],
                                                       order='id desc',limit=1)
        self.employee_wage=contract_record.wage


    def get_questions(self):
        lines=[(5,0,0)]
        for rec in self.env['rate.scale'].search([('is_hr_question','=',False)]):
            lines.append((0,0,{
                'questions':rec.questions
            }))
        self.update({'rating_scale_ids':lines})


    def hr_get_questions(self):
        lines=[(5,0,0)]
        for rec in self.env['rate.scale'].search([('is_hr_question','=',True)]):
            lines.append((0,0,{
                'questions':rec.questions
            }))
        self.update({'hr_rating_scale_ids':lines})





    def confirm_multi_appraisal(self):
        self.button_confirm()


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
