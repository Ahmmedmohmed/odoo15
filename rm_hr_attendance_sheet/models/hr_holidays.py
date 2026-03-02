# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrPublicHoliday(models.Model):
    _name = "hr.public.holiday"
    _inherit = ['mail.thread', 'mail.activity.mixin']  # إضافة activity.mixin لنسخة 15 لضمان عمل الأنشطة
    _description = "Public Holiday"

    HOLIDAY_TYPE = [
        ('emp', 'Employee'),
        ('dep', 'Department'),
        ('tag', 'Tags')
    ]

    type_select = fields.Selection(HOLIDAY_TYPE, "By", default='emp', tracking=True)

    # علاقات الـ Many2many سليمة، لكن أضفنا tracking لمتابعة التغييرات
    emp_ids = fields.Many2many(
        comodel_name="hr.employee",
        relation="employee_ph_rel",
        column1="employee_ph_col2",
        column2="attendance_ph_col2",
        string="Employees",
        tracking=True)

    dep_ids = fields.Many2many(
        comodel_name="hr.department",
        relation="department_att_ph_rel1",
        column1="ph_department_col2",
        column2="att_ph_col3",
        string="Departments")

    cat_ids = fields.Many2many(
        comodel_name="hr.employee.category",
        relation="category__phrel",
        column1="cat_col2",
        column2="ph_col2",
        string="Tags")

    name = fields.Char(string="Description", required=True, tracking=True)
    date_from = fields.Date(string="From", required=True, tracking=True)
    date_to = fields.Date(string="To", required=True, tracking=True)

    # في Odoo 15 نستخدم tracking=True بدلاً من track_visibility
    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Not Active')],
        default='inactive',
        string='Status',
        required=True,
        index=True,
        tracking=True)

    note = fields.Text("Notes")

    @api.onchange("dep_ids", "cat_ids", "type_select")
    def get_employee_ids(self):
        """ دالة تحديث قائمة الموظفين بناءً على القسم أو الوسوم لنسخة 15 """
        if self.type_select == 'dep' and self.dep_ids:
            employees = self.env['hr.employee'].search(
                [('department_id', 'in', self.dep_ids.ids)])
            self.emp_ids = [(6, 0, employees.ids)]  # استخدام نمط الـ Command للـ Many2many في 15
        elif self.type_select == 'tag' and self.cat_ids:
            employees = self.env['hr.employee'].search(
                [('category_ids', 'in', self.cat_ids.ids)])
            self.emp_ids = [(6, 0, employees.ids)]