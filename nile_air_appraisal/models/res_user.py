from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    # تحديد رتبة المستخدم في نظام التقييم
    appraisal_role = fields.Selection(
        string="Appraisal Role",
        selection=[
            ('user', 'User / Employee'),
            ('manager', 'Direct Manager'),
            ('hr', 'HR Manager'),
            ('co', 'CEO / CO'),
        ],
        default='user',
        help="Determines the access level in the Appraisal workflow."
    )