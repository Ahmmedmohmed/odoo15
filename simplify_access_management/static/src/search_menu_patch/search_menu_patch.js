/** @odoo-module **/
import { SearchBarMenu } from "@web/search/search_bar_menu/search_bar_menu";
const { patch } = require('web.utils'); // استخدم الطريقة المتوافقة مع 15
const { onWillStart, useState } = owl.hooks;

patch(SearchBarMenu.prototype, "my_custom_patch_name", {
  setup() {
    this._super(...arguments); // في 15 نستخدم _super وليس super.setup
    this.access = useState({
      removeCustomFilter: false,
      removeCustomGroup: false,
    });
    onWillStart(async () => {
      const res = await this.env.services.rpc({
        model: "access.management",
        method: "is_custom_filter_and_group_available",
        args: ["", this?.env?.searchModel?.resModel],
      });
      this.access.removeCustomFilter = res.filter;
      this.access.removeCustomGroup = res.group;
    });
  },
});