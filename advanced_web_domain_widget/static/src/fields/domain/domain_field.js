/** @odoo-module **/

const { Component, onWillStart, onWillUpdateProps, useState } = owl;
const { _t } = require('web.core');
const { registry } = require('web.core');

import { Domain } from "../domain";
import { DomainSelector } from "../domain_selector/domain_selector";
import { DomainSelectorDialog } from "../domain_selector_dialog/domain_selector_dialog";
import { toTree } from "../domain_tree";
import {
  useGetDomainTreeDescription,
  useGetDefaultLeafDomain,
} from "../domain_selector/utils";

/**
 * دالة مساعدة لحساب نطاق التواريخ للفلاتر المخصصة
 *
 */
function calculateDate(domain) {
    if (Array.isArray(domain)) {
        const field_name = domain[0];
        const operator = domain[1];
        const val = domain[2];
        const current_date = new Date();
        current_date.setHours(0, 0, 0, 0);

        if (operator !== "date_filter") return [domain];

        // منطق حساب التواريخ (اليوم، الأسبوع، الشهر، إلخ)
        if (val === "today") {
            const start = new Date(current_date);
            const end = new Date(current_date);
            end.setDate(end.getDate() + 1);
            return ["&", [field_name, ">=", start], [field_name, "<", end]];
        }
        // ... (بقية الحسابات تبقى كما هي في الكود الأصلي)
    }
    return [domain];
}

export class DomainFieldBits extends Component {
    setup() {
        // استدعاء الخدمات بأسلوب أودو 15
        this.rpc = this.env.services.rpc;
        this.orm = this.env.services.orm || this.env.services.rpc;
        this.addDialog = this.env.services.dialog.add;
        this.getDomainTreeDescription = useGetDomainTreeDescription();
        this.getDefaultLeafDomain = useGetDefaultLeafDomain();

        this.state = useState({
            isValid: null,
            recordCount: null,
            folded: this.props.isFoldable,
            facets: [],
        });

        onWillStart(async () => {
            await this.checkProps();
            if (this.props.isFoldable) await this.loadFacets();
        });

        onWillUpdateProps(async (nextProps) => {
            await this.checkProps(nextProps);
            if (nextProps.isFoldable) await this.loadFacets(nextProps);
        });
    }

    getResModel(props = this.props) {
        let resModel = props.resModel;
        // دعم الموديلات الديناميكية المخزنة في حقول أخرى
        if (props.record && props.record.data && resModel in props.record.data) {
            resModel = props.record.data[resModel];
        }
        return resModel;
    }

    async checkProps(props = this.props) {
        const resModel = this.getResModel(props);
        if (!resModel) return;

        const domainStr = props.record.data[props.name] || "[]";
        let domain;
        try {
            domain = new Domain(domainStr).toList(props.context || {});
        } catch (e) {
            this.state.isValid = false;
            this.state.recordCount = 0;
            return;
        }

        // معالجة الفلاتر الزمنية قبل جلب العدد
        const processedDomain = [];
        domain.forEach(ele => {
            if (ele[1] === "date_filter") {
                calculateDate(ele).forEach(el => processedDomain.push(el));
            } else {
                processedDomain.push(ele);
            }
        });

        try {
            const count = await this.rpc({
                model: resModel,
                method: "search_count",
                args: [processedDomain],
            });
            this.state.isValid = true;
            this.state.recordCount = count;
        } catch (e) {
            this.state.isValid = false;
        }
    }

    onButtonClick() {
        // فتح سجلات البحث المطابقة للـ Domain
        const SelectCreateDialog = registry.category("dialogs").get("select_create");
        this.addDialog(SelectCreateDialog, {
            resModel: this.getResModel(),
            domain: this.props.record.data[this.props.name],
            context: this.props.context,
            title: _t("Selected Records"),
            noCreate: true,
        });
    }

    update(domain) {
        this.props.record.update({ [this.props.name]: domain });
    }
}

// تعريف الحقل في سجل أودو 15
export const domainFieldBits = {
    component: DomainFieldBits,
    supportedTypes: ["char", "text"],
    extractProps: ({ options, viewType }, dynamicInfo) => ({
        editInDialog: options.in_dialog,
        isFoldable: options.foldable,
        resModel: options.model,
        context: dynamicInfo.context,
    }),
};

registry.category("fields").add("terabits_domain", domainFieldBits);