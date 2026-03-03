/** @odoo-module **/

import { CogMenu } from "@web/search/cog_menu/cog_menu";
// في أودو 15 نستخدم أداة الـ patch من web.utils لضمان الاستقرار
const { patch } = require('web.utils');
// استيراد الـ hooks من owl.hooks مباشرة في نسخة 15
const { useState } = owl.hooks;

patch(CogMenu.prototype, "simplify_access_management.CogMenuPatch", {
    /**
     * @override
     */
    setup() {
        // استخدام _super بدلاً من super.setup في أودو 15
        this._super(...arguments);

        // تعريف الحالة لمراقبة صلاحية الـ Spreadsheet
        this.access = useState({ removeSpreadsheet: false });

        const config = this.env.config || {};
        // التأكد من وجود الخدمات (services) قبل الاستدعاء
        if (config.actionType === "ir.actions.act_window" && this.env.services.rpc) {
            // نتحقق من السيرفر باستخدام rpc من البيئة مباشرة (النمط القياسي لـ V15)
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
     * في أودو 15، يعتمد CogMenu على getter يسمى items لتوليد القائمة
     */
    get items() {
        const items = this._super(...arguments);
        if (this.access.removeSpreadsheet) {
            // تصفية العناصر لحذف خيار Spreadsheet إذا لم يكن مسموحاً به
            return items.filter(item => {
                // التحقق من اسم المكون البرمجي في نسخة 15
                return item.Component && item.Component.name !== "SpreadsheetCogMenu";
            });
        }
        return items;
    }
});