/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";
import { useState, onWillStart } from "@odoo/owl";

patch(FormController.prototype, "simplify_access_management.FormControllerPatch", {
    setup() {
        this._super(...arguments);

        // تعريف الحالة لمراقبة الصلاحية
        this.access = useState({ removeProperty: false });

        onWillStart(async () => {
            try {
                // التأكد من وجود خدمة الـ rpc قبل الاستدعاء
                if (this.env.services.rpc) {
                    const res = await this.env.services.rpc({
                        model: "access.management",
                        method: "is_add_property_available",
                        args: [this.props.resModel],
                    });
                    this.access.removeProperty = res;
                }
            } catch (error) {
                console.error("Access Management FormController Error:", error);
            }
        });
    },

    /**
     * @override
     * تصفية قائمة الإجراءات (Actions)
     */
    get actionMenuItems() {
        const menuItems = this._super(...arguments);

        // التحقق من وجود القائمة والحالة قبل الفلترة لمنع أخطاء الـ undefined
        if (menuItems && menuItems.action && this.access && this.access.removeProperty) {
            menuItems.action = menuItems.action.filter(
                ele => ele.key !== "addPropertyFieldValue"
            );
        }
        return menuItems;
    }
});