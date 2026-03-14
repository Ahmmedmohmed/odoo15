/** @odoo-module **/

import { ActionMenus } from "@web/search/action_menus/action_menus";
import { patch } from "@web/core/utils/patch"; // الطريقة الصحيحة للاستيراد في Odoo 15 للمكونات الجديدة

patch(ActionMenus.prototype, "simplify_access_management.ActionMenusPatch", {
    /**
     * @override
     * في أودو 15، الدالة المسؤولة عن تجميع العناصر هي getActionItems
     */
    async getActionItems(props) {
        // استدعاء الدالة الأصلية
        const res = await this._super(...arguments);

        if (res && res.length > 0) {
            try {
                // استخدام rpc من env مباشرة لضمان التوافق مع نظام OWL في 15
                const RestActions = await this.env.services.rpc({
                    model: "access.management",
                    method: "get_remove_options",
                    args: [this.props.resModel],
                });

                const isExportHidden = await this.env.services.rpc({
                    model: "access.management",
                    method: "is_export_hide",
                    args: [this.props.resModel],
                });

                if (isExportHidden) {
                    return res.filter(
                        (ele) => !RestActions.includes(ele.key) && ele.key !== "export"
                    );
                }
                return res.filter((ele) => !RestActions.includes(ele.key));
            } catch (error) {
                console.error("Access Management Error:", error);
                return res; // في حالة الخطأ نرجع العناصر الأصلية عشان الشاشة ما تضربش
            }
        }
        return res;
    },
});