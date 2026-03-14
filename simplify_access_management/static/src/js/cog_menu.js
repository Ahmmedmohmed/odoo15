/** @odoo-module **/

import { CogMenu } from "@web/search/cog_menu/cog_menu";
import { patch } from "@web/core/utils/patch"; // الطريقة القياسية لـ V15 في نظام OWL
import { useState } from "@odoo/owl"; // استيراد useState من مكتبة owl مباشرة

patch(CogMenu.prototype, "simplify_access_management.CogMenuPatch", {
    /**
     * @override
     */
    setup() {
        this._super(...arguments);

        // تعريف الحالة لمراقبة صلاحية الـ Spreadsheet
        this.access = useState({ removeSpreadsheet: false });

        const config = this.env.config || {};

        // التأكد من وجود خدمة الـ rpc في أودو 15
        if (config.actionType === "ir.actions.act_window" && this.env.services.rpc) {
            this.env.services.rpc({
                model: "access.management",
                method: "is_spread_sheet_available",
                args: [config.actionType, config.actionId],
            }).then((res) => {
                this.access.removeSpreadsheet = res;
            }).catch((err) => {
                console.error("Access Management RPC Error:", err);
            });
        }
    },

    /**
     * @override
     * في أودو 15، يتم تصفية العناصر عبر getter الـ items
     */
    get items() {
        const items = this._super(...arguments);
        if (this.access && this.access.removeSpreadsheet) {
            // تصفية العناصر لحذف خيار Spreadsheet (غالباً يكون اسمه الإنشائي SpreadsheetCogMenu)
            return items.filter(item => {
                // نتحقق من وجود المكون واسمه البرمجي في نسخة 15
                return !item.Component || item.Component.name !== "SpreadsheetCogMenu";
            });
        }
        return items;
    }
});