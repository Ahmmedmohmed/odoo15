from odoo import models, fields, api,_
class HREmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    appraisal_number = fields.Integer(compute='compute_appraisal_number')


    def compute_appraisal_number(self):
        self.appraisal_number=0
        for rec in self:
            num=0
            for app in self.env['appraisal.appraisal'].search([('employee_id','=',rec.id)]):
                num+=1
            rec.appraisal_number=num


    def button_appraisal(self):
        return {
            'name': _('Appraisal'),
            'res_model': 'appraisal.appraisal',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=',self.id)],
            'type': 'ir.actions.act_window',
        }

