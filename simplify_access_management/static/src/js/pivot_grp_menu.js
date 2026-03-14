/** @odoo-module **/

import { PivotGroupByMenu } from "@web/views/pivot/pivot_group_by_menu";
import { patch } from "@web/core/utils/patch";
import { onWillStart } from "@odoo/owl";

patch(PivotGroupByMenu.prototype, "simplify_access_management.PivotPatch", {
    /**
     * @override
     */
    setup() {
        this._super(...arguments);

        onWillStart(async () => {
            try {
                // التأكد من وجود الموديل وخدمة الـ RPC
                if (this.env.searchModel && this.env.services.rpc) {
                    const hiddenFields = await this.env.services.rpc({
                        model: "access.management",
                        method: "get_hidden_field",
                        args: ["", this.env.searchModel.resModel],
                    });

                    if (hiddenFields && hiddenFields.length > 0) {
                        // فلترة الحقول المتاحة في الـ Pivot قبل العرض
                        // في V15، الحقول غالباً تكون موجودة في this.fields
                        if (this.fields) {
                            this.fields = this.fields.filter(
                                (field) => !hiddenFields.includes(field.name)
                            );
                        }
                    }
                }
            } catch (error) {
                console.error("Pivot GroupBy Access Error:", error);
            }
        });
    },
});