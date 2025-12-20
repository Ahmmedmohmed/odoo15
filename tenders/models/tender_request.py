from odoo import models, fields, api
from odoo.exceptions import UserError


class TenderRequest(models.Model):
    _name = 'tender.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    code = fields.Char(string="Tender Code", readonly=True)
    customer = fields.Many2one('res.partner', string='Customer', required=True)
    tender_purpose = fields.Char('الغرض من المناقصة', required=True)
    date = fields.Date('Date', required=True)
    tender_number = fields.Char('Tender Number', required=True)
    tender_amount = fields.Float('Tender Amount', required=True)
    bid_from = fields.Date('Bid from', required=True)
    bid_to = fields.Date('Bid to', required=True)
    project_id = fields.Many2one('project.project', string="Project")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approve_ceo', 'Approved (CEO)'),
        ('a_word', 'A Word'),
        ('not_a_word', 'Not a Word'),
        ('cancel', 'Cancel'),
        ('apologize', 'Apologize'),
        ('reject', 'Rejected'),
    ], readonly=True, default='draft', track_visibility='onchange')
    reason_of_not_a_word = fields.Char(
        string='Reason of not a word',
        readonly=1
    )
    reason_of_cancel = fields.Char(
        string='Reason of cancel',
        readonly=1
    )
    reason_of_apologize = fields.Char(
        string='Reason of apologize',
        readonly=1
    )
    contract_ids = fields.Many2many(
        'contract.contract'
    )

    def action_show_contract(self):
        for rec in self:
            domain = [('id', 'in', rec.contract_ids.ids)]
            view_tree = {
                'name': 'Contracts',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'contract.contract',
                'type': 'ir.actions.act_window',
                'domain': domain,
            }
            return view_tree

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_approve_ceo(self):
        self.write({'state': 'approve_ceo'})
        self.env['letters.of.guarantee.request'].create({
            'beneficiary': self.customer.id,
            'letter_purpose': self.tender_purpose + " - " + self.tender_number,
            'letter_value': self.tender_amount,
            'project_id': self.project_id.id if self.project_id else False,
        })

    def action_reject(self):
        self.write({'state': 'reject'})

    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('tender.request.sequence') or '/'
        return super(TenderRequest, self).create(vals)

    def unlink(self):
        for tender_request in self:
            if tender_request.state == 'approve_ceo':
                raise UserError("You cannot delete a tender request that has been approved.")
        return super(TenderRequest, self).unlink()

    def action_view_product_ids(self):
        order_id = self.env['project.project'].sudo()
        views = [(False, 'tree'), (False, 'form')]
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.project',
                'view_mode': 'form,tree',
                'view_type': 'form',
                'res_id': order_id.id,
                'views': views,
                'target': 'current',
                'domain': [('project_id', '=', rec.id)],
            }

    def name_get(self):
        result = []
        for account in self:
            name = 'Tender Request - ' + str(account.id)
            result.append((account.id, name))
        return result

    def action_a_word(self):
        contract = self.env['contract.contract'].create({
            'tender_request_id': self.id,
            'partner_id': self.customer.id,
            'tender_number': self.tender_number,
            'tender_purpose': self.tender_purpose,
        })
        self.state = 'a_word'
        self.contract_ids += contract

    def action_not_a_word(self):
        res = self.env.ref('tenders.action_wizard_not_a_word').read()[0]
        return res

    def action_cancel(self):
        res = self.env.ref('tenders.action_wizard_cancel').read()[0]
        return res

    def action_apologize(self):
        res = self.env.ref('tenders.action_wizard_apologize').read()[0]
        return res

