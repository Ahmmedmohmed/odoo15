/** @odoo-module **/
import { ActionMenus } from "@web/search/action_menus/action_menus";
const { patch } = require('web.utils'); // طريقة استدعاء الـ patch في 15

patch(ActionMenus.prototype, "simplify_access_management.ActionMenusPatch", {
    // في 15 الدالة اسمها غالباً _getActionItems أو يتم التعامل معها في الـ setup
    async getActionItems() {
        const res = await this._super(...arguments);
        if (res.length > 0) {
            // استخدام rpc بدلاً من orm.call المباشر لضمان التوافق
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
                    (ele) => !RestActions.includes(ele.key) && ele.key != "export"
                );
            }
            return res.filter((ele) => !RestActions.includes(ele.key));
        }
        return res;
    },
});