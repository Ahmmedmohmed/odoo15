/** @odoo-module **/

import FormRenderer from 'web.FormRenderer';
import session from 'web.session';

// في أودو 15، بما أننا نستخدم @odoo-module، نقوم بعمل include للمكون المستورد
FormRenderer.include({
    /**
     * @override
     */
    async _renderView() {
        const res = await this._super(...arguments);
        const self = this;

        // الحصول على معرف الشركة الحالي لضمان دقة الصلاحيات
        const company_id = session.user_context.allowed_company_ids ?
                           session.user_context.allowed_company_ids[0] : session.company_id;

        if (this.state && this.state.model && company_id) {
            // استخدام الـ RPC القياسي في الـ Widget
            this._rpc({
                model: "access.management",
                method: "get_chatter_hide_details",
                args: [session.uid, company_id, this.state.model],
            }).then(function (result) {
                // التحكم في أزرار الـ Chatter عبر JQuery (النمط القياسي لـ V15)
                if (result) {
                    if (result.hide_send_mail) {
                        self.$el.find(".o_chatter_button_new_message").remove();
                    }
                    if (result.hide_log_notes) {
                        self.$el.find(".o_chatter_button_log_note").remove();
                    }
                    if (result.hide_schedule_activity) {
                        self.$el.find(".o_chatter_button_schedule_activity").remove();
                    }
                }
            }).catch(function (error) {
                console.error("Chatter Hide RPC Error:", error);
            });
        }
        return res;
    },
});