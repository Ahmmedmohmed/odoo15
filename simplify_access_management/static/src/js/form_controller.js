/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
const { patch } = require('web.utils');
const { useState, onWillStart } = owl.hooks;

patch(FormController.prototype, "simplify_access_management.FormControllerPatch", {
    setup() {
        this._super(...arguments);
        const self = this;
        // تعريف الحالة لمراقبة صلاحية إخفاء الخصائص أو أي إجراء مشابه في 15
        this.access = useState({ removeProperty: false });

        onWillStart(async () => {
            // استخدام rpc بدلاً من orm.call لضمان عملها على Odoo 15
            const res = await this.env.services.rpc({
                model: "access.management",
                method: "is_add_property_available",
                args: [this.props.resModel],
            });
            self.access.removeProperty = res;
        });
    },

    // في أودو 15، يتم الوصول لقائمة الإجراءات عبر actionMenuItems أيضاً في مكونات OWL
    get actionMenuItems() {
        const menuItems = this._super(...arguments);
        if (menuItems && menuItems.action && this.access.removeProperty) {
            // فلترة القائمة لاستبعاد خيار إضافة الخصائص (إن وجد في نسخة 15 المطورة)
            menuItems.action = menuItems.action.filter(
                ele => ele.key !== "addPropertyFieldValue"
            );
        }
        return menuItems;
    }
});