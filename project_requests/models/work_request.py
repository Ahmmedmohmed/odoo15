
from odoo import fields, models, api, _


class WorkRequest(models.Model):

    _name = "work.request"
    _rec_name = 'vehicle_request_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    vehicle_request_id = fields.Many2one(
        'vehicle.request'
    )
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
    work_request_lines = fields.One2many(
        'work.request.line',
        'work_request_id'
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Open'),
         ('closed', 'Closed')],
        default='draft',
        tracking=True
    )

    open_date = fields.Datetime(
        readonly=True
    )
    close_date = fields.Datetime(
        readonly=True
    )
    duration = fields.Float(
        string="Duration (Hours)",
        compute='_compute_duration',
        store=True,
        # digits=(12, 6)
    )

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('work.request') or _('New')
        return super(WorkRequest, self).create(vals)

    def re_sequence_wo_record_records(self):
        """Re-sequence all records using ir.sequence"""
        # Fetch all records ordered by creation date
        records = self.env['work.request'].search([], order='create_date ASC')
        for r in records:
            r.name = ""

        # Track already used sequences to avoid duplicates
        existing_sequences = set(records.mapped('name'))

        for record in records:
            # Skip if record already has a valid sequence (not 'New' or empty)
            if record.name and record.name != _('New') and record.name != 'New':
                continue

            # Generate new sequence
            new_sequence = self.env['ir.sequence'].next_by_code('work.request')

            # Make sure we don't create duplicates
            while new_sequence in existing_sequences:
                new_sequence = self.env['ir.sequence'].next_by_code('work.request')

            # Update record
            record.write({'name': new_sequence})
            existing_sequences.add(new_sequence)

            # _logger.info(f"Updated record ID {record.id} with sequence {new_sequence}")

        return True



    def action_open(self):
            for rec in self:
                rec.state = 'open'
                rec.open_date = fields.datetime.now()
                if rec.user_id:
                    activity_vals = {
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'summary': 'Work Request opened',
                        'note': 'This work request is Opined ',
                        'date_deadline': fields.Date.today(),
                        'res_id': rec.id,
                        'res_model_id': self.env.ref('project_requests.model_work_request').id,
                        'user_id': rec.user_id.id,
                    }
                    self.env['mail.activity'].create(activity_vals)
            project = self.env['project.project'].search([('id', '=', self.project_id.id)])
            print("project_follow  ", project)
            if project:
                # project_follow.date = fields.Date.today()

                equipment_lines = []
                for line in self.work_request_lines:
                    equipment_lines.append((0, 0, {
                        'fleet_id': line.fleet_id.id,
                        'supplier_id': line.supplier_id.id,
                        'vehicle_type_id': line.vehicle_type_id.id,
                        'qty': line.qty,
                        'note': line.note,
                        # 'from_request_work': True,
                    }))
                    line.opened = True
                project.write({
                    'equipment_request_id': equipment_lines
                })

    def action_close(self):
        for rec in self:
            rec.state = 'closed'
            rec.close_date = fields.datetime.now()
            if rec.user_id:
                activity_vals = {
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'summary': 'Work Request closed',
                    'note': 'This work request is closed ',
                    'date_deadline': fields.Date.today(),
                    'res_id': rec.id,
                    'res_model_id': self.env.ref('project_requests.model_work_request').id,
                    'user_id': rec.user_id.id,
                }
                self.env['mail.activity'].create(activity_vals)


    @api.depends('open_date', 'close_date', 'state')
    def _compute_duration(self):
        for rec in self:
            if rec.open_date and rec.close_date and rec.state == 'closed':
                delta = rec.close_date - rec.open_date
                # Calculate total hours including fractional hours
                rec.duration = delta.total_seconds() / 3600
            else:
                rec.duration = 0.0




class WorkRequestLine(models.Model):

    _name = "work.request.line"

    work_request_id = fields.Many2one(
        'work.request'
    )
    description = fields.Char(
        # required=True
    )

    vehicle_type_id = fields.Many2one(
        'vehicle.type'
    )
    fleet_id = fields.Many2one(
        'fleet.vehicle',
        string='نوع المعدة'
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

    closed = fields.Boolean(string="Close")
    opened = fields.Boolean(string="Opened")

    def action_open_from_lines(self):
        project = self.env['project.project'].search([('id', '=', self.work_request_id.project_id.id)])
        print("project_follow  ", project)
        if project:
            # project_follow.date = fields.Date.today()

            equipment_lines = []
            for line in self:
                equipment_lines.append((0, 0, {
                    'fleet_id': line.fleet_id.id,
                    'supplier_id': line.supplier_id.id,
                    'vehicle_type_id': line.vehicle_type_id.id,
                    'qty': line.qty,
                    'note': line.note,
                    # 'from_request_work': True,
                }))
                line.opened = True
            project.write({
                'equipment_request_id': equipment_lines
            })
