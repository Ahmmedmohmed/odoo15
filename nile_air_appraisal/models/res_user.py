from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    appraisal_role = fields.Selection(
        selection=[
            ('user', 'Employee'),
            ('manager', 'Direct Manager'),
            ('hr', 'HR Manager'),
            ('co', 'CEO / CO'),
        ],
        string="Appraisal Role",
        default='user'
    )