# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _


class ProjectFollow(models.Model):

    _name = "project.follow"
    _description = "Project Follow"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'project_id'

    user_id = fields.Many2one(
        'res.users',
        string='Accountant'
        , tracking=True
        # default=lambda self: self.env.user,
        # readonly=1
    )
    site_engineer = fields.Many2one(
        'res.users',
        string='Site Engineer'
        , tracking=True
    )
    manager_id = fields.Many2one(
        'res.users',
        string='Project Manager'
        , tracking=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer'
        , tracking=True
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project Name',
        required=1
        , tracking=True
    )
    sequence = fields.Char(
        string='Sequence',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
        , tracking=True
    )
    new_sequence = fields.Char(
        compute='compute_new_sequence',
        string="Sequence"
        , tracking=True
    )
    date = fields.Date(
        default=fields.Date.today()
        , tracking=True
    )
    daily_supplies_id = fields.One2many(
        'daily.supplies',
        'daily_project_follow_id'
        , tracking=True
    )
    remaining_quantities_id = fields.One2many(
        'remaining.quantities',
        'remaining_project_follow_id'
        , tracking=True
    )
    result_quantities_id = fields.One2many(
        'result.quantities',
        'result_project_follow_id'
        , tracking=True
    )
    executed_works_id = fields.One2many(
        'executed.works',
        'executed_project_follow_id'
        , tracking=True
    )
    heavy_equipment_id = fields.One2many(
        'heavy.equipment',
        'heavy_project_follow_id'
        , tracking=True
    )
    problems_equipment_id = fields.One2many(
        'project.problems',
        'problems_project_follow_id'
        , tracking=True
    )
    exchange_quantity = fields.Float(
        compute='compute_exchange_quantity',
        store=1 , tracking=True
    )
    cumulative_exchange_quantity = fields.Float(
        compute='compute_exchange_quantity',
        store=1 , tracking=True
    )

    is_locked = fields.Boolean(string='Locked', default=False, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm')],default='draft' , tracking=True)


    def action_lock_report_form(self):
        for rec in self:
            rec.is_locked = True
            rec.state = 'confirm'


    @api.depends('daily_supplies_id')
    def compute_exchange_quantity(self):
        for rec in self:
            if rec.daily_supplies_id:
                rec.exchange_quantity = rec.daily_supplies_id[0].exchange_quantity
                rec.cumulative_exchange_quantity = rec.daily_supplies_id[0].cumulative_exchange_quantity
            else:
                rec.exchange_quantity = 0
                rec.cumulative_exchange_quantity = 0

    def compute_new_sequence(self):
        for rec in self:
            rec.new_sequence = str(rec.project_id.name) + '/' + str(rec.sequence)

    @api.model
    def create(self, vals):
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('project.follow') or _('New')

        res = super(ProjectFollow, self).create(vals)

        if res.heavy_equipment_id:
            for line in res.heavy_equipment_id:
                vehicle = line.fleet_id
                if vehicle:
                    vehicle.sudo().odometer_unit = line.selected_unit

                    # Create odometer record via ORM
                    odometer = self.env['fleet.vehicle.odometer'].sudo().create({
                        'date': fields.Date.today(),
                        'vehicle_id': vehicle.id or False,
                        'value': line.work_hours,
                        'project_id': res.project_id.id,
                        'make': vehicle.f_brand_id.id if vehicle.f_brand_id else False,
                        'model': vehicle.model_id.id if vehicle.model_id else False,
                    })

                    # If you really need the ID of the created record
                    odometer_id = odometer.id
                    # no need for fetchone or commit

        return res
    @api.onchange('project_id')
    @api.constrains('project_id')
    def onchange_project_id(self):
        for rec in self:
            # rec.manager_id = rec.project_id.user_id.id
            rec.partner_id = rec.project_id.partner_id.id
