from odoo import fields, api, models


class ProjectProblems(models.Model):
    _name = 'project.problems'

    problem = fields.Char(
        string='المشكلة',
        required=True
    )
    reason = fields.Char(
        string='سبب المشكلة'
    )
    solution = fields.Char(
        string='الحلول المقترحة'
    )
    note = fields.Text(
        string="ملاحظات"
    )
    problems_project_follow_id = fields.Many2one(
        'project.follow'
    )

    @api.model
    def create(self, vals):
        res = super(ProjectProblems, self).create(vals)
        # Post message to parent
        if res.problems_project_follow_id:
            body = f"Line added: {res.problem} "
            res.problems_project_follow_id.message_post(body=body)
        return res

    def write(self, vals):
        # Track changes before write
        for record in self:
            old_values = {
                'reason': record.reason,
                'solution': record.solution,
            }

        res = super(ProjectProblems, self).write(vals)

        # Post changes to parent
        for record in self:
            changes = []
            if 'reason' in vals and old_values['reason'] != record.reason:
                changes.append(f"Reason: {old_values['reason']} → {record.reason}")
            if 'solution' in vals and old_values['solution'] != record.solution:
                changes.append(f"Solution: {old_values['solution']} → {record.solution}")


            if changes and record.problems_project_follow_id:
                body = "Line updated:<br/>" + "<br/>".join(changes)
                record.problems_project_follow_id.message_post(body=body)

        return res

    def unlink(self):
        # Track deletion
        for record in self:
            if record.problems_project_follow_id:
                body = f"Line deleted: {record.problem} "
                record.problems_project_follow_id.message_post(body=body)
        return super(ProjectProblems, self).unlink()
