/** @odoo-module **/
import { FormRenderer } from "web.FormRenderer";
import { session } from "web.session";

// في أودو 15 نستخدم الـ include لتعديل الـ Widgets القديمة
FormRenderer.include({
    async _renderView() {
        const res = await this._super(...arguments);
        const self = this;

        // استخراج الشركة الحالية من الـ Session أو الـ URL
        const company_id = session.user_context.allowed_company_ids ? session.user_context.allowed_company_ids[0] : session.company_id;

        if (this.state.model && company_id) {
            this._rpc({
                model: "access.management",
                method: "get_chatter_hide_details",
                args: [session.uid, company_id, this.state.model],
            }).then(function (result) {
                // استخدام JQuery للتحكم في عناصر الـ Chatter في 15
                if (result && !result.hide_send_mail) {
                    self.$el.find(".o_chatter_button_new_message").remove();
                }
                if (result && !result.hide_log_notes) {
                    self.$el.find(".o_chatter_button_log_note").remove();
                }
                if (result && !result.hide_schedule_activity) {
                    self.$el.find(".o_chatter_button_schedule_activity").remove();
                }
            });
        }
        return res;
    },
});