
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class VehicleRequest(models.Model):

    _name = "vehicle.request"
    _rec_name = 'project_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    project_id = fields.Many2one(
        'project.project',
        string='المشروع'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer'
    )
    date = fields.Date()
    company_id = fields.Many2one(
        'res.company'
    )
    user_id = fields.Many2one(
        'res.users',
        string='Project Manager'
    )
    tag_ids = fields.Many2many(
        'project.tags',
        string='Tags'
    )
    vehicle_request_lines = fields.One2many(
        'vehicle.request.line',
        'vehicle_id'
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirmed', 'Confirmed')],
        default='draft',
        tracking=True
    )

    def action_confirm(self):
        for rec in self:
            lines = []
            if rec.vehicle_request_lines:
                for line in rec.vehicle_request_lines:
                    line = (0, 0, {
                        'description': line.description,
                        'vehicle_type_id': line.vehicle_type_id.id,
                        'fleet_id': line.fleet_id.id,
                        'qty': line.qty,
                        'tag_ids': line.tag_ids.ids,
                        'note': line.note,
                        'supplier_id': line.supplier_id.id,
                    })
                    lines.append(line)
                work_request = self.env['work.request'].create({
                    'vehicle_request_id': rec.id,
                    'project_id': rec.project_id.id,
                    'partner_id': rec.partner_id.id,
                    'date': rec.date,
                    'company_id': rec.company_id.id,
                    'user_id': rec.user_id.id,
                    'tag_ids': rec.tag_ids.ids,
                    'work_request_lines': lines,
                })
                rec.state = 'confirmed'
            else:
                raise ValidationError(_('يجب إنشاء طلب معدة أولاً !'))


class VehicleRequestLine(models.Model):

    _name = "vehicle.request.line"

    vehicle_id = fields.Many2one(
        'vehicle.request'
    )
    vehicle_type_id = fields.Many2one(
        'vehicle.type'
    )
    description = fields.Char(
        # required=True
    )
    fleet_id = fields.Many2one(
        'fleet.vehicle',
        string=' المعدة'
    )
    fleet_model_id = fields.Many2one(
        'fleet.vehicle.model',
        string='الموديل',
        related='fleet_id.model_id'
    )
    qty = fields.Float(
        string='العدد المطلوب',
        required=True,
    )
    tag_ids = fields.Many2many(
        comodel_name="project.tags",
        string="العلامات"
    )
    note = fields.Char(
        string="ملاحظات"
    )
    supplier_id = fields.Many2one(
        'res.partner',
        string='المورد'
    )

    # @api.constrains('fleet_id')
    # def _check_fleet_id(self):
    #     for rec in self:
    #         open_request = self.env['work.request'].search([
    #             ('state', '=', 'open')
    #         ])
    #         if open_request:
    #             open_fleet = open_request.work_request_lines.mapped('fleet_id')
    #             if rec.fleet_id in open_fleet and open_request.work_request_lines.closed == False:
    #                 raise ValidationError(_('هذه المعدة موجوده في أمر شغل مفتوح حالياً !'))
    #

    @api.constrains('fleet_id')
    def _check_fleet_id(self):
        for rec in self:
            open_requests = self.env['work.request'].search([
                ('state', '=', 'open')
            ])
            for request in open_requests:
                open_fleet = request.work_request_lines.mapped('fleet_id')
                if rec.fleet_id in open_fleet and any(not line.closed for line in request.work_request_lines):
                    raise ValidationError(_('هذه المعدة موجودة في أمر شغل مفتوح حالياً !'))
