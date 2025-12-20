from email.policy import default
from datetime import timedelta

from odoo import _, api, fields, models, tools
from odoo.exceptions import AccessError ,ValidationError


class HelpdeskTicket(models.Model):
    _name = "helpdesk.ticket"
    _description = "Helpdesk Ticket"
    _rec_name = "number"
    _order = "priority desc, sequence, number desc, id desc"
    _mail_post_access = "read"
    _inherit = ["mail.thread.cc", "mail.activity.mixin", "portal.mixin"]

    @api.depends("team_id")
    def _compute_stage_id(self):
        for ticket in self:
            ticket.stage_id = ticket.team_id._get_applicable_stages()[:1]
            # if ticket.stage_id in ['','','']:



    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """Show always the stages without team, or stages of the default team."""
        search_domain = [
            "|",
            ("id", "in", stages.ids),
            ("team_ids", "=", False),
        ]
        default_team_id = self.default_get(["team_id"]).get("team_id")
        if default_team_id:
            search_domain = [
                "|",
                ("team_ids", "=", default_team_id),
            ] + search_domain
        return stages.search(search_domain, order=order)

    number = fields.Char(string="Ticket number", default="/", readonly=True)
    name = fields.Char(string="Title", required=True)
    description = fields.Html(required=True, sanitize_style=True)
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Assigned user",
        tracking=True,
        index=True,
        domain="team_id and [('share', '=', False),('id', 'in', user_ids)] or [('share', '=', False)]",  # noqa: B950
    )
    user_ids = fields.Many2many(
        comodel_name="res.users", related="team_id.user_ids", string="Users"
    )
    stage_id = fields.Many2one(
        comodel_name="helpdesk.ticket.stage",
        string="Stage",
        compute="_compute_stage_id",
        store=True,
        readonly=False,
        ondelete="restrict",
        tracking=True,
        group_expand="_read_group_stage_ids",
        copy=False,
        index=True,
        domain="['|',('team_ids', '=', team_id),('team_ids','=',False)]",
    )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Contact")
    partner_name = fields.Char()
    partner_email = fields.Char(string="Email")
    last_stage_update = fields.Datetime(default=fields.Datetime.now)
    assigned_date = fields.Datetime()
    closed_date = fields.Datetime()
    closed = fields.Boolean(related="stage_id.closed")
    unattended = fields.Boolean(related="stage_id.unattended", store=True)
    tag_ids = fields.Many2many(comodel_name="helpdesk.ticket.tag", string="Tags")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    channel_id = fields.Many2one(
        comodel_name="helpdesk.ticket.channel",
        string="Channel",
        help="Channel indicates where the source of a ticket"
        "comes from (it could be a phone call, an email...)",
    )
    category_id = fields.Many2one(
        comodel_name="helpdesk.ticket.category",
        string="Category",
    )
    team_id = fields.Many2one(
        comodel_name="helpdesk.ticket.team",
        string="Team",
        index=True,
    )
    priority = fields.Selection(
        selection=[
            ("0", "Low"),
            ("1", "Medium"),
            ("2", "High"),
            ("3", "Very High"),
        ],
        default="1",
    )
    attachment_ids = fields.One2many(
        comodel_name="ir.attachment",
        inverse_name="res_id",
        domain=[("res_model", "=", "helpdesk.ticket")],
        string="Media Attachments",
    )
    color = fields.Integer(string="Color Index")
    kanban_state = fields.Selection(
        selection=[
            ("normal", "Default"),
            ("done", "Ready for next stage"),
            ("blocked", "Blocked"),
        ],
    )
    sequence = fields.Integer(
        index=True,
        default=10,
        help="Gives the sequence order when displaying a list of tickets.",
    )
    active = fields.Boolean(default=True)

    # is_personal_user = fields.Boolean(compute="_compute_user_group", store=False)
    # is_team_user = fields.Boolean(compute="_compute_user_group", store=False)
    # is_top_user = fields.Boolean(compute="_compute_user_group", store=False)

    # ############################################################################################
    is_personal_user = fields.Boolean(
        default=lambda self: self.env.user.has_group('helpdesk_mgmt.group_helpdesk_user_own'),
        compute="_compute_user_access",
        store=False
    )
    is_team_user = fields.Boolean(
        default=lambda self: self.env.user.has_group('helpdesk_mgmt.group_helpdesk_user_team'),
        compute="_compute_user_access",
        store=False
    )
    is_top_user = fields.Boolean(
        default=lambda self: self.env.user.has_group('helpdesk_mgmt.group_helpdesk_user'),
        compute="_compute_user_access",
        store=False
    )

    @api.depends_context('uid')
    @api.depends('create_uid')
    def _compute_user_access(self):
        current_user = self.env.user

        # Check user groups
        has_personal_group = current_user.has_group('helpdesk_mgmt.group_helpdesk_user_own')
        has_team_group = current_user.has_group('helpdesk_mgmt.group_helpdesk_user_team')
        has_top_group = current_user.has_group('helpdesk_mgmt.group_helpdesk_user')

        for rec in self:
            # Top users have access to everything
            if has_top_group:
                rec.is_top_user = True
                rec.is_team_user = True
                rec.is_personal_user = True
            else:
                rec.is_top_user = False

                # Team users have access to team records
                if has_team_group:
                    # Add your team logic here
                    rec.is_team_user = True
                    rec.is_personal_user = has_personal_group
                else:
                    rec.is_team_user = False

                    # Personal users only have access to their own records
                    if has_personal_group:
                        rec.is_personal_user = (rec.create_uid.id == current_user.id if rec.create_uid else True)
                    else:
                        rec.is_personal_user = False
    # ############################################################################################


    employee_name = fields.Char(string="Employee",related='create_uid.name', store=True)
    # user_department = fields.Many2one(related='user_id.department_id',string="Department")

    tickit_period = fields.Char(string="Tickit Period",compute="_compute_tickets_period")

    from datetime import timedelta

    @api.depends('closed_date', 'assigned_date')
    def _compute_tickets_period(self):
        for rec in self:
            if rec.closed_date and rec.assigned_date:
                delta = rec.closed_date - rec.assigned_date
                total_seconds = delta.total_seconds()
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                rec.tickit_period = f"{hours} hours, {minutes} minutes"
            else:
                rec.tickit_period = " "

    # def _compute_user_group(self):
    #     """Compute group membership flags for the current user"""
    #     print("start")
    #     for rec in self:
    #         rec.is_personal_user = self.env.user.has_group('helpdesk_mgmt.group_helpdesk_user_own')
    #         rec.is_team_user = self.env.user.has_group('helpdesk_mgmt.group_helpdesk_user_team')
    #         rec.is_top_user = self.env.user.has_group('helpdesk_mgmt.group_helpdesk_user')

    # @api.onchange("name","write_date")
    # @api.depends("create_uid","write_uid")
    # def _compute_user_group(self):
    #     for rec in self:
    #         print("start")
    #
    #         tickit_personal_user = self.env.user.has_group('helpdesk_mgmt.group_helpdesk_user_own')
    #         tickit_team_user = self.env.user.has_group('helpdesk_mgmt.group_helpdesk_user_team')
    #         tickit_top_user = self.env.user.has_group('helpdesk_mgmt.group_helpdesk_user')
    #         # manager = self.env.user.has_group('helpdesk_mgmt.group_helpdesk_manager')
    # #         # unallowed_user = self.env.user.has_group('helpdesk_mgmt.group_unallowed_user')
    # #
    #         print("tickit_personal_user == ",tickit_personal_user)
    #         print("tickit_team_user  ===== ",tickit_team_user)
    #         print("user ================== ",tickit_top_user)
    #         print("manager",manager)
    #         # print("unallowed_user",unallowed_user)
    #         # print("unallowed_user",unallowed_user)
    #
    #
    #         # print("tickit_user",tickit_user)
    #         if tickit_team_user and not user:
    #             rec.is_tickit_user = True
    #             rec.is_manager = False
    #             rec.is_user = False
    #         elif user and not manager:
    #             rec.is_user = True
    #             rec.is_manager = False
    #             rec.is_tickit_user = False
    #         # elif manager and not unallowed_user:
    #         #     rec.is_manager = True
    #         #     rec.is_user = False
    #         #     rec.is_tickit_user = False
    #         else:
    #             rec.is_manager = True
    #             rec.is_user = False
    #             rec.is_tickit_user = False
    #




    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, rec.number + " - " + rec.name))
        return res

    def assign_to_me(self):
        self.write({"user_id": self.env.user.id})

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if self.partner_id:
            self.partner_name = self.partner_id.name
            self.partner_email = self.partner_id.email

    # ---------------------------------------------------
    # CRUD
    # ---------------------------------------------------

    def _creation_subtype(self):
        return self.env.ref("helpdesk_mgmt.hlp_tck_created")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("number", "/") == "/":
                vals["number"] = self._prepare_ticket_number(vals)
            if vals.get("user_id") and not vals.get("assigned_date"):
                vals["assigned_date"] = fields.Datetime.now()
        return super().create(vals_list)

    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if "number" not in default:
            default["number"] = self._prepare_ticket_number(default)
        res = super().copy(default)
        return res

    def write(self, vals):
        for _ticket in self:
            now = fields.Datetime.now()
            if vals.get("stage_id"):
                stage = self.env["helpdesk.ticket.stage"].browse([vals["stage_id"]])
                vals["last_stage_update"] = now
                if stage.closed:
                    vals["closed_date"] = now
            if vals.get("user_id"):
                vals["assigned_date"] = now

            for ticket in self:
                old_stage_sequence = ticket.stage_id.sequence

                if old_stage_sequence >= 4:

                    new_stage = self.env["helpdesk.ticket.stage"].browse(vals['stage_id'])
                    new_stage_sequence = new_stage.sequence if new_stage else 0

                    if new_stage_sequence < old_stage_sequence:
                        raise ValidationError(" You can't go back to the previous stage ")

        return super().write(vals)


    def action_duplicate_tickets(self):
        for ticket in self.browse(self.env.context["active_ids"]):
            ticket.copy()

    def _prepare_ticket_number(self, values):
        seq = self.env["ir.sequence"]
        if "company_id" in values:
            seq = seq.with_company(values["company_id"])
        return seq.next_by_code("helpdesk.ticket.sequence") or "/"

    def _compute_access_url(self):
        res = super()._compute_access_url()
        for item in self:
            item.access_url = "/my/ticket/%s" % (item.id)
        return res

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------

    def _track_template(self, tracking):
        res = super()._track_template(tracking)
        ticket = self[0]
        if "stage_id" in tracking and ticket.stage_id.mail_template_id:
            res["stage_id"] = (
                ticket.stage_id.mail_template_id,
                {
                    # Need to set mass_mail so that the email will always be sent
                    "composition_mode": "mass_mail",
                    "auto_delete_message": True,
                    "subtype_id": self.env["ir.model.data"]._xmlid_to_res_id(
                        "mail.mt_note"
                    ),
                    "email_layout_xmlid": "mail.mail_notification_light",
                },
            )
        return res

    @api.model
    def message_new(self, msg, custom_values=None):
        """Override message_new from mail gateway so we can set correct
        default values.
        """
        if custom_values is None:
            custom_values = {}
        defaults = {
            "name": msg.get("subject") or _("No Subject"),
            "description": msg.get("body"),
            "partner_email": msg.get("from"),
            "partner_id": msg.get("author_id"),
        }
        defaults.update(custom_values)

        # Write default values coming from msg
        ticket = super().message_new(msg, custom_values=defaults)

        # Use mail gateway tools to search for partners to subscribe
        email_list = tools.email_split(
            (msg.get("to") or "") + "," + (msg.get("cc") or "")
        )
        partner_ids = [
            p.id
            for p in self.env["mail.thread"]._mail_find_partner_from_emails(
                email_list, records=ticket, force_create=False
            )
            if p
        ]
        ticket.message_subscribe(partner_ids)

        return ticket

    def message_update(self, msg, update_vals=None):
        """Override message_update to subscribe partners"""
        email_list = tools.email_split(
            (msg.get("to") or "") + "," + (msg.get("cc") or "")
        )
        partner_ids = [
            p.id
            for p in self.env["mail.thread"]._mail_find_partner_from_emails(
                email_list, records=self, force_create=False
            )
            if p
        ]
        self.message_subscribe(partner_ids)
        return super().message_update(msg, update_vals=update_vals)

    def _message_get_suggested_recipients(self):
        recipients = super()._message_get_suggested_recipients()
        try:
            for ticket in self:
                if ticket.partner_id:
                    ticket._message_add_suggested_recipient(
                        recipients, partner=ticket.partner_id, reason=_("Customer")
                    )
                elif ticket.partner_email:
                    ticket._message_add_suggested_recipient(
                        recipients,
                        email=ticket.partner_email,
                        reason=_("Customer Email"),
                    )
        except AccessError:
            # no read access rights -> just ignore suggested recipients because this
            # imply modifying followers
            return recipients
        return recipients

    def _notify_get_reply_to(
        self, default=None, records=None, company=None, doc_names=None
    ):
        """Override to set alias of tasks to their team if any."""
        aliases = (
            self.sudo()
            .mapped("team_id")
            ._notify_get_reply_to(
                default=default, records=None, company=company, doc_names=None
            )
        )
        res = {ticket.id: aliases.get(ticket.team_id.id) for ticket in self}
        leftover = self.filtered(lambda rec: not rec.team_id)
        if leftover:
            res.update(
                super(HelpdeskTicket, leftover)._notify_get_reply_to(
                    default=default, records=None, company=company, doc_names=doc_names
                )
            )
        return res
