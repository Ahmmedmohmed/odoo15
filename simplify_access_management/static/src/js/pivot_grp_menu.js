/** @odoo-module **/
import { PivotGroupByMenu } from "@web/views/pivot/pivot_group_by_menu";
const { patch } = require('web.utils');

patch(PivotGroupByMenu.prototype, "simplify_access_management.PivotPatch", {
    setup() {
        this._super(...arguments);
        const self = this;
        // في OWL 1 نستخدم hooks مختلفة أو نعتمد على الـ onWillStart المتاحة
        this.env.services.rpc({
            model: "access.management",
            method: "get_hidden_field",
            args: ["", this.env.searchModel.resModel],
        }).then((res) => {
            if (res && res.length > 0) {
                self.fields = self.fields.filter((ele) => !res.includes(ele.name));
                // إجبار المكون على إعادة الرسم في OWL 1
                self.render();
            }
        });
    },
});