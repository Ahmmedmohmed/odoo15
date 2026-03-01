/** @odoo-module **/

const { Component } = owl;
const { _t } = require('web.core');
const { registry } = require('web.core');

// استيراد المكونات الأساسية
import { AutoComplete } from "@web/core/autocomplete/autocomplete";
import { Domain } from "@web/core/domain";

const SEARCH_LIMIT = 7;
const SEARCH_MORE_LIMIT = 320;

export class RecordAutocomplete extends Component {
    setup() {
        // في أودو 15 نصل للخدمات عبر this.env.services
        this.orm = this.env.services.orm || this.env.services.rpc;
        this.nameService = this.env.services.name;

        // إدارة النوافذ المنبثقة (Dialogs) في أودو 15
        this.addDialog = this.env.services.dialog.add;

        this.sources = [
            {
                placeholder: _t("Loading..."),
                options: this.loadOptionsSource.bind(this),
            },
        ];
    }

    addNames(nameGets) {
        const displayNames = {};
        for (const [id, label] of nameGets) {
            displayNames[id] = label.split("\n")[0];
        }
        this.nameService.addDisplayNames(this.props.resModel, displayNames);
    }

    getIds() {
        return this.props.getIds() || [];
    }

    async loadOptionsSource(name) {
        // البحث عن السجلات بناءً على النص المدخل
        const nameGets = await this.search(name, SEARCH_LIMIT + 1);

        // دعم القيم الافتراضية للبيئة (Environment context)
        if (this.props.resModel === "res.users") {
            nameGets.push([0, _t("Environment user")]);
        }
        if (this.props.resModel === "res.company") {
            nameGets.push([0, _t("Environment company")]);
        }

        this.addNames(nameGets);

        const options = nameGets.map(([value, label]) => ({
            value,
            label: label.split("\n")[0]
        }));

        // إضافة خيار "البحث عن المزيد" إذا تجاوزت النتائج الحد المسموح
        if (SEARCH_LIMIT < nameGets.length) {
            options.push({
                label: _t("Search More..."),
                action: this.onSearchMore.bind(this, name),
                classList: "o_m2o_dropdown_option",
            });
        }

        if (options.length === 0) {
            options.push({ label: _t("(no result)"), unselectable: true });
        }
        return options;
    }

    async onSearchMore(name) {
        const { fieldString, multiSelect, resModel } = this.props;
        let operator;
        const ids = [];

        if (name) {
            const nameGets = await this.search(name, SEARCH_MORE_LIMIT);
            this.addNames(nameGets);
            operator = "in";
            ids.push(...nameGets.map((nameGet) => nameGet[0]));
        } else {
            operator = "not in";
            ids.push(...this.getIds());
        }

        const dynamicFilters = ids.length ? [{
            description: _t("Quick search: %s").replace('%s', name),
            domain: [["id", operator, ids]],
        }] : undefined;

        // فتح نافذة الاختيار (Select/Create Dialog) الخاصة بأودو 15
        const SelectCreateDialog = registry.category("dialogs").get("select_create");
        this.addDialog(SelectCreateDialog, {
            title: _t("Search: %s").replace('%s', fieldString),
            dynamicFilters,
            resModel,
            noCreate: true,
            multiSelect,
            context: this.props.context || {},
            onSelected: (resId) => {
                const resIds = Array.isArray(resId) ? resId : [resId];
                this.props.update([...resIds]);
            },
        });
    }

    getDomain() {
        const domainIds = Domain.not([["id", "in", this.getIds()]]);
        if (this.props.domain) {
            return Domain.and([this.props.domain, domainIds]).toList();
        }
        return domainIds.toList();
    }

    onSelect({ value: resId, action }, params) {
        if (action) {
            return action(params);
        }
        this.props.update([resId]);
    }

    search(name, limit) {
        const domain = this.getDomain();
        // استخدام rpc العادي في أودو 15 لضمان التوافق
        return this.env.services.rpc({
            model: this.props.resModel,
            method: "name_search",
            kwargs: {
                name,
                args: domain,
                limit,
                context: this.props.context || {},
            }
        });
    }

    onChange({ inputValue }) {
        if (!inputValue.length) {
            this.props.update([]);
        }
    }
}

// تعريف الخصائص والمكونات لـ OWL 1
RecordAutocomplete.template = "web.RecordAutocomplete";
RecordAutocomplete.components = { AutoComplete };
RecordAutocomplete.props = {
    resModel: String,
    update: Function,
    multiSelect: Boolean,
    getIds: Function,
    value: { type: String, optional: true },
    domain: { type: Array, optional: true },
    context: { type: Object, optional: true },
    className: { type: String, optional: true },
    fieldString: { type: String, optional: true },
    placeholder: { type: String, optional: true },
};