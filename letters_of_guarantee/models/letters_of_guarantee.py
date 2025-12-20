from odoo import fields, models, api
from datetime import timedelta
from odoo.exceptions import ValidationError


class LettersOfGuarantee(models.Model):
    _name = 'letters.of.guarantee'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'letter_number'

    bank = fields.Char('Bank')
    letter_type = fields.Selection(
        [('primary', 'ابتدائي'),
         ('ultimate', 'نهائي'),
         ('advance_payment', 'دفعة مقدمة')],
        string="نوع خطاب الضمان"
    )
    beneficiary = fields.Many2one(
        'res.partner'
    )
    customer_id = fields.Many2one(
        'contract.contract',
        string="Contract"
    )
    letter_number = fields.Char(
        'Letter Number'
    )
    release_date = fields.Date(
        'Release Date'
    )
    letter_length = fields.Integer(
        string='مدة الخطاب'

    )
    purpose = fields.Char(
        string="الغرض من الخطاب (الموضوع)")
    old_expiry_date = fields.Date(
        string='Expiry Date'
    )
    expiry_date = fields.Date(
        compute='_compute_expiry_date',
        string='New Expiry Date'
    )
    extend = fields.Integer(
        default=0,
        string='فترة التمديد'
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project'
    )
    letter_value = fields.Float(
        string="قيمة خطاب الضمان"
    )
    insurance_value = fields.Float(
        compute='_compute_insurance_value',
        store=True,
        string='قيمة التأمين'
    )
    percentage = fields.Float(
        string="نسبة التأمين%"
    )
    percentage_more = fields.Float(
        string="نسبة تعلية خطاب الضمان %"
    )
    insurance_value_more = fields.Float(
        compute='_compute_insurance_value_more',
        store=True,
        string='قيمة تعلية خضاب الضمان'
    )
    total_letter_of_guarantee_value = fields.Float(
        compute='_compute_total_letter_of_guarantee_value',
        string=' Total Letter of Guarantee Value'
    )

    height_insurance_value = fields.Float(
        compute='_compute_height_insurance_value',
        string=' قيمة تأمين التعلية '
    )

    total_insurance_value_after_increase = fields.Float(
        compute='_compute_total_insurance_value_after_increase',
        string=' اجمالي قيمة التامين بعد التعلية  '
    )

    letter_state = fields.Selection(
        [('in_progress', 'In Progress'),
         ('expired', 'Expired')],
        string='Letter State'
    )
    bank_response_date = fields.Date(
        'Bank Response Date'
    )
    bank_response = fields.Char(
        'Bank Response'
    )
    state = fields.Selection(
        [('extended', 'تعليه'),
         ('returned', 'مردود')]
    )
    request_id = fields.Many2one(
        'letters.of.guarantee.request'
    )
    end_date_extension_line = fields.One2many(
        'guarantee.extension.line',
        'guarantee_id'
    )
    is_appear_return = fields.Boolean(
        default=False
    )
    date = fields.Date(
        string='Date',
        default=fields.Date.today()
    )
    bank_letters_of_guarantee_id = fields.Many2one(
        'bank.letters.of.guarantee',
        string='Bank'
    )
    account_move_ids = fields.Many2many(
        'account.move',
        copy=False
    )
    account_move_count = fields.Integer(
        compute='compute_account_move_count'
    )
    is_more = fields.Boolean(
        default=False
    )

    @api.depends('letter_value', 'percentage_more')
    def _compute_insurance_value_more(self):
        for rec in self:
            rec.insurance_value_more = rec.percentage_more / 100 * rec.letter_value

    @api.depends('insurance_value_more', 'letter_value')
    def _compute_total_letter_of_guarantee_value(self):
        for rec in self:
            rec.total_letter_of_guarantee_value = rec.insurance_value_more + rec.letter_value

    @api.depends('percentage', 'insurance_value_more')
    def _compute_height_insurance_value(self):
        for rec in self:
            rec.height_insurance_value = rec.insurance_value_more * rec.percentage / 100

    @api.depends('height_insurance_value', 'insurance_value')
    def _compute_total_insurance_value_after_increase(self):
        for rec in self:
            rec.total_insurance_value_after_increase = rec.height_insurance_value + rec.insurance_value

    def compute_account_move_count(self):
        for rec in self:
            account_move_count = self.env['account.move'].search_count([
                ('id', 'in', rec.account_move_ids.ids)
            ])
            if account_move_count:
                rec.account_move_count = account_move_count
            else:
                rec.account_move_count = 0

    def action_show_journal_entry(self):
        action = self.env.ref('account.action_move_journal_line').read()[0]
        if self.account_move_count > 1:
            action['context'] = "{'default_journal_type': 'bank'}"
            action['domain'] = [('journal_id.type', '=', 'bank'), ('id', 'in', self.account_move_ids.ids)]
        elif self.account_move_count == 1:
            action['views'] = [(self.env.ref('contract.view_account_move_contract_helper_form').id, 'form')]
            action['res_id'] = self.account_move_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_approve_cfo(self):
        if not self.bank_letters_of_guarantee_id:
            raise ValidationError('Please choose the bank of guarantee !')
        accounting_record = self.env['account.letters.of.guarantee'].search([], limit=1)
        if accounting_record:
            lines = [(0, 0, {'account_id': accounting_record.account_id.id,
                             'debit': self.insurance_value,
                             'credit': 0.0,
                             'partner_id': self.beneficiary.id,
                             }),
                     (0, 0, {'account_id': self.bank_letters_of_guarantee_id.journal_id.default_account_id.id,
                             'debit': 0.0,
                             'credit': self.insurance_value,
                             'partner_id': self.beneficiary.id,
                             })]
            move = self.env['account.move'].create({
                'move_type': 'entry',
                'ref': 'Letters Of Guarantee' + '/' + str(self.id),
                'date': self.date,
                'journal_id': self.bank_letters_of_guarantee_id.journal_id.id,
                'line_ids': lines
            })
            self.account_move_ids += move
        else:
            raise ValidationError('Please enter the account in configuration !')
        self.is_appear_return = True

    def action_extend(self):
        if not self.bank_letters_of_guarantee_id:
            raise ValidationError('Please choose the bank of guarantee !')
        if self.letter_value <= 0:
            raise ValidationError('The letter value must be greater than zero !')
        if self.percentage_more <= 0:
            raise ValidationError('! نسبة التعليه يجب أن تكون أكبر من صفر')
        accounting_record = self.env['account.letters.of.guarantee'].search([], limit=1)
        if accounting_record:
            lines = [(0, 0, {'account_id': accounting_record.account_id.id,
                             'debit': self.insurance_value_more,
                             'credit': 0.0,
                             'partner_id': self.beneficiary.id,
                             }),
                     (0, 0, {'account_id': self.bank_letters_of_guarantee_id.journal_id.default_account_id.id,
                             'debit': 0.0,
                             'credit': self.insurance_value_more,
                             'partner_id': self.beneficiary.id,
                             })]
            move = self.env['account.move'].create({
                'move_type': 'entry',
                'ref': 'Letters Of Guarantee' + '/' + str(self.id),
                'date': self.date,
                'journal_id': self.bank_letters_of_guarantee_id.journal_id.id,
                'line_ids': lines
            })
            self.account_move_ids += move
        else:
            raise ValidationError('Please enter the account in configuration !')
        self.state = 'extended'
        self.is_more = True

    def action_return(self):
        if not self.bank_letters_of_guarantee_id:
            raise ValidationError('Please choose the bank of guarantee !')
        accounting_record = self.env['account.letters.of.guarantee'].search([], limit=1)
        if accounting_record:
            lines = [(0, 0, {'account_id': self.bank_letters_of_guarantee_id.journal_id.default_account_id.id,
                             'debit': self.insurance_value + self.insurance_value_more if self.is_more else self.insurance_value,
                             'credit': 0.0,
                             'partner_id': self.beneficiary.id,
                             }),
                     (0, 0, {'account_id': accounting_record.account_id.id,
                             'debit': 0.0,
                             'credit': self.insurance_value + self.insurance_value_more if self.is_more else self.insurance_value,
                             'partner_id': self.beneficiary.id,
                             })]
            move = self.env['account.move'].create({
                'move_type': 'entry',
                'ref': 'Letters Of Guarantee' + '/' + str(self.id),
                'date': self.date,
                'journal_id': self.bank_letters_of_guarantee_id.journal_id.id,
                'line_ids': lines
            })
            self.account_move_ids += move
        else:
            raise ValidationError('Please enter the account in configuration !')
        self.state = 'returned'

    @api.depends('letter_value', 'percentage')
    def _compute_insurance_value(self):
        for rec in self:
            rec.insurance_value = rec.percentage / 100 * rec.letter_value

    # @api.depends('release_date', 'extend', 'letter_length')
    # def _compute_expiry_date(self):
    #     for record in self:
    #         if record.release_date and record.letter_length:
    #             length = record.letter_length + record.extend
    #             record.expiry_date = record.release_date + timedelta(days=length)
    #         else:
    #             record.expiry_date = False

    @api.depends('end_date_extension_line')
    def _compute_expiry_date(self):
        for rec in self:
            lines = rec.env['guarantee.extension.line'].sudo().search(
                [('guarantee_id', '=', rec.id), ('check', '=', True)])
            if lines:
                rec.expiry_date = lines[-1].new_extension_date
            else:
                rec.expiry_date = False


class Project(models.Model):
    _inherit = 'project.project'

    def action_open_letters_of_guarantee(self):
        letters_of_guarantee = self.env['letters.of.guarantee'].search([('project_id', '=', self.id)])
        action = self.env.ref('letters_of_guarantee.action_letters_of_guarantee').read()[0]
        action['domain'] = [('id', 'in', letters_of_guarantee.ids)]
        return action


class GuaranteeExtensionDateLine(models.Model):
    _name = 'guarantee.extension.line'
    _description = 'Guarantee Date Line'

    name = fields.Char(
        string="name"
    )
    new_extension_date = fields.Date(
        string="New Expiry Date"
    )
    check = fields.Boolean(
        string="Check"
    )
    guarantee_id = fields.Many2one(
        'letters.of.guarantee'
    )
