/** @odoo-module **/

import { MultiRecordSelector } from "./multi_record_selector";
import { RecordSelector } from "./record_selector";
import { Expression } from "../domain_tree";
const { _t } = require('web.core');
const { formatAST, toPyValue } = require('web.py_utils');

// دالة التحقق من المعرف (ID)
export const isId = (val) => Number.isInteger(val) && val >= 1;

// دالة تنسيق العرض والألوان
export const getFormat = (val, displayNames, resModel="") => {
    let text;
    let colorIndex;
    // دعم خاص للمستخدم والشركة الحاليين (القيمة 0)
    if (isId(val) || (['res.users', 'res.company'].includes(resModel) && val === 0)) {
        text = typeof displayNames[val] === "string"
                ? displayNames[val]
                : _t("Inaccessible/missing record ID: %s", val);
        colorIndex = typeof displayNames[val] === "string" ? 0 : 2;
    } else {
        text = val instanceof Expression
                ? String(val)
                : _t("Invalid record ID: %s", formatAST(toPyValue(val)));
        colorIndex = val instanceof Expression ? 2 : 1;
    }
    return { text, colorIndex };
};

// مكون الاختيار المتعدد (Multi-Select)
export class DomainSelectorAutocomplete extends MultiRecordSelector {
    getIds(props = this.props) {
        return props.resIds.filter((val) => isId(val));
    }

    getTags(props, displayNames) {
        return props.resIds.map((val, index) => {
            // التعامل مع الرموز الخاصة Environment User/Company
            if (['res.users', 'res.company'].includes(this.props.resModel) && val === 0) {
                displayNames[val] = this.props.resModel === 'res.users' ? _t("Environment User") : _t("Environment Company");
            }
            const { text, colorIndex } = getFormat(val, displayNames, this.props.resModel);
            return {
                text,
                colorIndex,
                onDelete: () => {
                    this.props.update([
                        ...this.props.resIds.slice(0, index),
                        ...this.props.resIds.slice(index + 1),
                    ]);
                },
            };
        });
    }
}

// تعريف الـ Props لـ OWL 1
DomainSelectorAutocomplete.props = Object.assign({}, MultiRecordSelector.props, {
    resModel: { type: String, optional: true },
    resIds: { type: Array },
});

// مكون الاختيار الفردي (Single Select)
export class DomainSelectorSingleAutocomplete extends RecordSelector {
    getDisplayName(props = this.props, displayNames) {
        const { resId } = props;
        if (resId === false) {
            return "";
        }
        if (['res.users', 'res.company'].includes(this.props.resModel) && resId === 0) {
            displayNames[resId] = this.props.resModel === 'res.users' ? _t("Environment User") : _t("Environment Company");
        }
        const { text } = getFormat(resId, displayNames, this.props.resModel);
        return text;
    }

    getIds(props = this.props) {
        if (isId(props.resId)) {
            return [props.resId];
        }
        return [];
    }
}

DomainSelectorSingleAutocomplete.props = Object.assign({}, RecordSelector.props, {
    resId: { type: [Number, Boolean, String, Object] },
});