/** @odoo-module **/

import { CogMenu } from "@web/search/cog_menu/cog_menu";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
// في أودو 15، useState موجودة داخل owl مباشرة
const { useState } = owl;



patch(CogMenu.prototype, "simplify_access_management.CogMenuPatch", {
    /**
     * @override
     */
    setup() {
        this._super(...arguments);
        // استخدام خدمة rpc الرسمية في أودو 15
        this.rpc = useService("rpc");
        this.access = useState({ removeSpreadsheet: false });

        const config = this.env.config || {};
        if (config.actionType === "ir.actions.act_window") {
            // نتحقق من السيرفر إذا كان يجب إخفاء Spreadsheet
            this.rpc({
                model: "access.management",
                method: "is_spread_sheet_available",
                args: [config.actionType, config.actionId],
            }).then((res) => {
                this.access.removeSpreadsheet = res;
            });
        }
    },

    /**
     * @override
     * في أودو 15، CogMenu بيعتمد على getter اسمه items لجلب العناصر
     */
    get items() {
        const items = this._super(...arguments);
        if (this.access.removeSpreadsheet) {
            // تصفية العناصر لحذف مكون SpreadsheetCogMenu إذا لم يكن مسموحاً به
            return items.filter(item => item.Component.name !== "SpreadsheetCogMenu");
        }
        return items;
    }
});