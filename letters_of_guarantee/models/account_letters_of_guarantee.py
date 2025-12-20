from odoo import fields, api, models, _


class AccountLettersOfGuarantee(models.Model):
    _name = 'account.letters.of.guarantee'

    account_id = fields.Many2one(
        'account.account',
        string='غطاء خطابات الضمان'
    )
    # account_purchase_id = fields.Many2one(
    #     'account.account',
    #     string='مصروفات خطاب الضمان'
    # )
