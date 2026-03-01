/** @odoo-module **/

import { ModelFieldSelector } from "web.ModelFieldSelector";
const { patch } = require('web.utils');

// ملاحظة: في أودو 15، قد يكون المكون Popover مدمجاً أو يتبع بنية مختلفة قليلاً
// لذا سنركز على تعديل المكون الأساسي لضمان الفلترة

patch(ModelFieldSelector.prototype, "simplify_access_management.FieldSelectorPatch", {
    setup() {
        this._super(...arguments);
        // في أودو 15، نستخدم rpc مباشرة من البيئة (env)
    },

    // تعديل الدالة المسؤولة عن جلب الحقول المتاحة للاختيار
    async _loadFields(model, path) {
        const fields = await this._super(...arguments);

        // استدعاء دالة البايثون لجلب الحقول المخفية
        const hiddenFields = await this.env.services.rpc({
            model: "access.management",
            method: "get_hidden_field",
            args: ["", model],
        });

        if (hiddenFields && hiddenFields.length > 0) {
            // فلترة قائمة الحقول قبل عرضها للمستخدم
            return fields.filter(field => !hiddenFields.includes(field.name));
        }
        return fields;
    },

    // حماية الحالة لمنع اختيار حقل محظور يدوياً أو عبر الـ Path
    async _updatePath(path) {
        const model = this.props.resModel;
        const hiddenFields = await this.env.services.rpc({
            model: "access.management",
            method: "get_hidden_field",
            args: ["", model],
        });

        if (hiddenFields && hiddenFields.includes(path) && path !== "id") {
            // تحويل المسار لـ id في حال كان الحقل محظوراً
            return this._super("id");
        }
        return this._super(...arguments);
    }
});