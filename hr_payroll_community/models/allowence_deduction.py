
from collections import defaultdict
from datetime import datetime, date, time
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AllowanceDeductionModel(models.Model):
    _name = 'allowance.deduction'
    _rec_name = 'employee_id'
    _description = 'New Description'

    date = fields.Date(string="Date", )
    employee_id = fields.Many2one(comodel_name="hr.employee",
                                  string="Employee",
                                  compute='value_employee_id_badg',
                                  store=True
                                  )
    badge = fields.Char(string="Badge Id", required=True)
    quantity = fields.Float(string="Amount", )
    input_id = fields.Many2one(comodel_name="hr.payslip.input.type", )
    description = fields.Text(string="Description", required=False, )

    @api.depends('badge')
    def value_employee_id_badg(self):
        for rec in self:
            if rec.badge:
                employees = self.env['hr.employee'].search([('barcode', '=', rec.badge)])
                if employees:
                    for emp in employees:
                        rec.employee_id = emp.id
                else:
                    rec.employee_id = False
            else:
                rec.employee_id = False


class AllowanceDeductionModelLine(models.Model):
    _name = 'allowance.deduction.line'

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=False, )
    badge = fields.Char(string="Badge Id", required=False, )
    quantity = fields.Float(string="Quantity",)
    rule_id = fields.Many2one(comodel_name="hr.salary.rule",)
    description = fields.Text(string="Description", required=False, )
    allowance_id = fields.Many2one(comodel_name="allowance.deduction", string="", required=False, )

    @api.onchange('allowance_id', 'allowance_id.type','rule_id')
    def filter_rule_id(self):
        lines = []
        print("JJJJJJJJJJJJJJJJJJJJJJJJJJJJ")
        for rec in self.env['hr.salary.rule'].search([]):
            if rec.category_id.name == self.allowance_id.type:
                lines.append(rec.id)
        # for lin in self.allowence_deduction_ids:
        return {
            'domain': {'rule_id': [('id', 'in', lines)]}
        }

#########################################################################
# class HrPayslipEmployees(models.TransientModel):
#     _inherit = 'hr.payslip.employees'
#
#     def compute_sheet(self):
#         self.ensure_one()
#         if not self.env.context.get('active_id'):
#             from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
#             end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
#             payslip_run = self.env['hr.payslip.run'].create({
#                 'name': from_date.strftime('%B %Y'),
#                 'date_start': from_date,
#                 'date_end': end_date,
#             })
#         else:
#             payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))
#
#         employees = self.with_context(active_test=False).employee_ids
#         if not employees:
#             raise UserError(_("You must select employee(s) to generate payslip(s)."))
#
#         payslips = self.env['hr.payslip']
#         Payslip = self.env['hr.payslip']
#
#         contracts = employees._get_contracts(payslip_run.date_start, payslip_run.date_end, states=['open', 'close'])
#         contracts._generate_work_entries(payslip_run.date_start, payslip_run.date_end)
#         work_entries = self.env['hr.work.entry'].search([
#             ('date_start', '<=', payslip_run.date_end),
#             ('date_stop', '>=', payslip_run.date_start),
#             ('employee_id', 'in', employees.ids),
#         ])
#         self._check_undefined_slots(work_entries, payslip_run)
#
#         validated = work_entries.action_validate()
#         if not validated:
#             work_entries_by_contract = defaultdict(lambda: self.env['hr.work.entry'])
#             for work_entry in work_entries.filtered(lambda w: w.state == 'conflict'):
#                 work_entries_by_contract[work_entry.contract_id] |= work_entry
#
#             for contract, work_entries in work_entries_by_contract.items():
#                 conflicts = work_entries._to_intervals()
#                 time_intervals_str = "\n - ".join(['', *["%s -> %s" % (s[0], s[1]) for s in conflicts._items]])
#             raise UserError(
#                 _("Some work entries of employee %s could not be validated. Time intervals to look for:%s") % (
#                 contract.employee_id.name, time_intervals_str))
#
#         default_values = Payslip.default_get(Payslip.fields_get())
#         for contract in contracts:
#             values = dict(default_values, **{
#                 'employee_id': contract.employee_id.id,
#                 'credit_note': payslip_run.credit_note,
#                 'payslip_run_id': payslip_run.id,
#                 'date_from': payslip_run.date_start,
#                 'date_to': payslip_run.date_end,
#                 'contract_id': contract.id,
#                 'struct_id': self.structure_id.id or contract.structure_type_id.default_struct_id.id,
#             })
#             payslip = self.env['hr.payslip'].new(values)
#             payslip._onchange_employee()
#             payslip.update_other_inputs()
#             values = payslip._convert_to_write(payslip._cache)
#             payslips += Payslip.create(values)
#
#         # payslips.compute_work_hours()
#         # payslips.compute_sheet()
#
#         payslip_run.state = 'verify'
#
#         # payslips.compute_hour_amount()
#         # payslips.compute_all_cycle()
#
#         return {
#             'type': 'ir.actions.act_window',
#             'res_model': 'hr.payslip.run',
#             'views': [[False, 'form']],
#             'res_id': payslip_run.id,
#         }
######################################################################################################

class hr_salary_rule(models.Model):
    _inherit = 'hr.payslip'
    #
    @api.onchange('employee_id','date_from','date_to')
    def update_other_inputs(self):
        lines_list = [(5,0,0)]
        payslip_other_input = self.env['allowance.deduction'].search([('date', '>=', self.date_from), ('date', '<=', self.date_to),('employee_id','=',self.employee_id.id)])
        for inp in payslip_other_input:
            lines_list.append((0, 0,{
                                       'name':inp.input_id.name,
                                       'code':inp.input_id.code,
                                        'amount':inp.quantity,
                                        'contract_id':inp.employee_id.contract_id.id ,
                                }))
        self.update({'input_line_ids': lines_list})


    # def compute_sheet(self):
    #     res = super(hr_salary_rule, self).compute_sheet()
    #
    #     if self.line_ids:
    #         import_payslips_line = self.env['allowance.deduction'].search(
    #             [('date', '>=', self.date_from), ('date', '<=', self.date_to)])
    #         lines_list = []
    #         for line in import_payslips_line:
    #             for rule in line.allowence_deduction_ids:
    #                 if rule.employee_id.id==self.employee_id.id:
    #                     lines_list.append((0,0, {
    #                                        'name': rule.rule_id.name,
    #                                        'code': rule.rule_id.code,
    #                                        'category_id': rule.rule_id.id,
    #                                        'salary_rule_id': rule.rule_id.id,
    #                                        'amount': rule.quantity,
    #                     }))
    #         self.update({'line_ids' :lines_list})
    #
    #     return res
