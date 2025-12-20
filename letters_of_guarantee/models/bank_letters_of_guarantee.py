from odoo import fields, api, models, _


class BankLettersOfGuarantee(models.Model):
    _name = 'bank.letters.of.guarantee'
    _rec_name = 'journal_id'

    journal_id = fields.Many2one(
        'account.journal',
        domain="[('type', '=', 'bank')]",
        string='البنك'
    )
