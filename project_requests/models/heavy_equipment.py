from odoo import fields, api, models


class HeavyEquipment(models.Model):
    _name = 'heavy.equipment'

    fleet_id = fields.Many2one(
        'fleet.vehicle',
        string='المعدة'
    )
    related_fleet_id = fields.Many2one(
        string='المعدة',
        related='fleet_id',
        readonly=False,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='المورد'
    )
    work_hours = fields.Float(
        string='عدد ساعات العمل'
    )
    waiting_time = fields.Float(
        string='وقت الانتظار'
    )
    total_work_hours = fields.Float(
        string='عدد ساعات العمل التراكمية',
        readonly=1
    )
    unit = fields.Many2one(
        'item.item',
        string='الوحدة'
    )
    selected_unit = fields.Selection(
        [('kilometers', 'km'),
         ('miles', 'Hours')],
        string="الوحدة",
        # required=1,
        default='kilometers'
    )


    rosary = fields.Selection([
        ('am', 'ص'),
        ('pm', 'م')],
        string="الوردية"
    )
    work = fields.Char(
        string='مكان وطبيعة العمل'
    )
    reason = fields.Text(
        string="سبب العطل ان وجد"
    )
    note = fields.Text(
        string="ملاحظات"
    )
    heavy_project_follow_id = fields.Many2one(
        'project.follow'
    )

    @api.model
    def create(self, vals):
        res = super(HeavyEquipment, self).create(vals)
        if res.heavy_project_follow_id:
            body = f"Line added: {res.fleet_id.name} "
            res.heavy_project_follow_id.message_post(body=body)

        project_follow_records = self.env['project.follow'].search([
            ('project_id', '=', res.heavy_project_follow_id.project_id.id)
        ])
        res.total_work_hours = sum(project_follow_records.mapped('heavy_equipment_id.work_hours'))
        return res



    def write(self, vals):
        # Track changes before write
        for record in self:
            old_values = {
                'fleet_id': record.fleet_id.name if record.fleet_id else False,
                'work_hours': record.work_hours,
                'waiting_time': record.waiting_time,
                'unit': record.unit.name,
                'rosary': record.rosary,
                'work': record.work,
                'reason': record.reason,
            }

        res = super(HeavyEquipment, self).write(vals)

        # Post changes to parent
        for record in self:
            changes = []
            if 'fleet_id' in vals and old_values['fleet_id'] != record.fleet_id.name:
                changes.append(f"Fleet: {old_values['fleet_id']} → {record.fleet_id.name}")
            if 'work_hours' in vals and old_values['work_hours'] != record.work_hours:
                changes.append(f"Work Hours: {old_values['work_hours']} → {record.work_hours}")
            if 'waiting_time' in vals and old_values['waiting_time'] != record.waiting_time:
                changes.append(f"Waiting Time: {old_values['waiting_time']} → {record.waiting_time}")
            if 'unit' in vals and old_values['unit'] != record.unit.name:
                changes.append(f"Unit: {old_values['unit']} → {record.unit.name}")
            if 'rosary' in vals and old_values['rosary'] != record.rosary:
                changes.append(f"Rosary: {old_values['rosary']} → {record.rosary}")
            if 'work' in vals and old_values['work'] != record.work:
                changes.append(f"Work: {old_values['work']} → {record.work}")
            if 'reason' in vals and old_values['reason'] != record.reason:
                changes.append(f"Reason: {old_values['reason']} → {record.reason}")

            if changes and record.heavy_project_follow_id:
                body = "Line updated:<br/>" + "<br/>".join(changes)
                record.heavy_project_follow_id.message_post(body=body)

        return res

    def unlink(self):
        # Track deletion
        for record in self:
            if record.heavy_project_follow_id:
                body = f"Line deleted: {record.fleet_id.name} "
                record.heavy_project_follow_id.message_post(body=body)
        return super(HeavyEquipment, self).unlink()
