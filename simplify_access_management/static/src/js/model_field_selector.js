/** @odoo-module **/

import ModelFieldSelector from "web.ModelFieldSelector";
import { patch } from "@web/core/utils/patch";

// في أودو 15، نقوم بعمل Patch للمكون المستورد مباشرة
// مع التأكد من أن المكون موجود في ذاكرة المتصفح
if (ModelFieldSelector) {
    patch(ModelFieldSelector.prototype, "simplify_access_management.FieldSelectorPatch", {
        /**
         * @override
         * تعديل الدالة المسؤولة عن جلب الحقول المتاحة للاختيار
         */
        async _loadFields(model, path) {
            const fields = await this._super(...arguments);

            try {
                // استدعاء دالة البايثون لجلب الحقول المخفية عبر خدمة الـ rpc في 15
                const hiddenFields = await this.env.services.rpc({
                    model: "access.management",
                    method: "get_hidden_field",
                    args: ["", model],
                });

                if (hiddenFields && hiddenFields.length > 0) {
                    // فلترة قائمة الحقول قبل عرضها للمستخدم
                    return fields.filter(field => !hiddenFields.includes(field.name));
                }
            } catch (error) {
                console.error("FieldSelector Access Error:", error);
            }
            return fields;
        },

        /**
         * @override
         * حماية الحالة لمنع اختيار حقل محظور يدوياً
         */
        async _updatePath(path) {
            const model = this.props.resModel;
            try {
                const hiddenFields = await this.env.services.rpc({
                    model: "access.management",
                    method: "get_hidden_field",
                    args: ["", model],
                });

                if (hiddenFields && hiddenFields.includes(path) && path !== "id") {
                    // إذا كان الحقل محظوراً، نمنع التحديث أو نوجهه لـ id
                    return this._super("id");
                }
            } catch (error) {
                console.error("Path Update Access Error:", error);
            }
            return this._super(...arguments);
        }
    });
}