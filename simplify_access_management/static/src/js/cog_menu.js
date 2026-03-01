/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { CogMenu } from "@web/search/cog_menu/cog_menu";
import { registry } from "@web/core/registry";

import { onWillStart, useState } from "@odoo/owl";
const cogMenuRegistry = registry.category("cogMenu");

patch(CogMenu.prototype, {
    setup() { 
        super.setup(); 
        var self = this;
        this.access = useState({removeSpreadsheet: false}); 
        if(this?.env?.config?.actionType == "ir.actions.act_window") {
            this.orm.call(
                "access.management",
                "is_spread_sheet_available",
                [1, this?.env?.config?.actionType, this?.env?.config?.actionId]
            ).then(async function(res){
                self.access.removeSpreadsheet = res;
                self.registryItems = await self._registryItems();
            }); 
        } 
    },
    async _registryItems() {
        const items = [];
        for (const item of cogMenuRegistry.getAll()) {
            if(item?.Component?.name === "SpreadsheetCogMenu" && this.access.removeSpreadsheet)
                continue;
            if ("isDisplayed" in item ? await item.isDisplayed(this.env) : true) {
                items.push({
                    Component: item.Component,
                    groupNumber: item.groupNumber,
                    key: item.Component.name,
                });
            }
        }
        return items;
    }
})/** @odoo-module **/

import { CogMenu } from "@web/search/cog_menu/cog_menu";
const { patch } = require('web.utils');
const { useState, onWillStart } = owl.hooks; // في 15 الـ hooks موجودة داخل owl.hooks

patch(CogMenu.prototype, "simplify_access_management.CogMenuPatch", {
    setup() {
        this._super(...arguments);
        const self = this;
        // تعريف الحالة لمراقبة الصلاحية
        this.access = useState({ removeSpreadsheet: false });

        // التحقق من نوع الإجراء الحالي
        if (this.env.config && this.env.config.actionType === "ir.actions.act_window") {
            // استخدام rpc بدلاً من orm.call المباشر لضمان التوافق مع 15
            this.env.services.rpc({
                model: "access.management",
                method: "is_spread_sheet_available",
                args: [1, this.env.config.actionType, this.env.config.actionId],
            }).then(function (res) {
                self.access.removeSpreadsheet = res;
                // في أودو 15 قد تحتاج لإعادة تحميل العناصر أو تحديث الحالة لإعادة الرسم
            });
        }
    },

    // إعادة تعريف جلب العناصر من الـ Registry مع الفلترة
    _registryItems() {
        const items = this._super(...arguments);
        // فلترة العناصر: إذا كان العنصر هو Spreadsheet ومطلوب حذفه، نقوم بإزالته من المصفوفة
        return items.filter(item => {
            if (item.Component && item.Component.name === "SpreadsheetCogMenu" && this.access.removeSpreadsheet) {
                return false;
            }
            return true;
        });
    }
});