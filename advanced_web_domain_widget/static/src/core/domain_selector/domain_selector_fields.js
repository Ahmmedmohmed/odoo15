/** @odoo-module **/

const { Component } = owl;
const { _t } = require('web.core');
const { registry } = require('web.core');
// في أودو 15 نستخدم web.time بدلاً من l10n/dates
const { serializeDate, serializeDateTime, deserializeDate, deserializeDateTime } = require('web.time');
const { evaluateExpr, formatAST } = require('web.py_utils');

import { selectOperators } from "./domain_selector_operators";
import { DateSelectionBits } from "../../dateSelectionBits/dateSelectionBits";
import { Expression, formatValue } from "../domain_tree";
import { DomainSelectorAutocomplete, DomainSelectorSingleAutocomplete } from "./domain_selector_autocomplete";

// أودو 15 بيعتمد على Moment.js للتعامل مع التواريخ
const moment = window.moment;

// ============================================================================
// المكونات الأساسية (Components) بأسلوب OWL 1
// ============================================================================

export class Editor extends Component {
    get stringifiedValue() {
        return formatValue(this.props.value);
    }
}
Editor.template = "advanced_web_domain_widget.DomainSelector.Editor";
Editor.props = ["info", "value", "update", "fieldDef"];

export class PathEditor extends Editor {
    get isSupportedPath() {
        const { path } = this.props;
        return [0, 1].includes(path) || typeof path === "string";
    }
    get stringifiedPath() {
        return formatValue(this.props.path);
    }
    onClear() {
        this.props.update();
    }
}
PathEditor.template = "advanced_web_domain_widget.DomainSelector.PathEditor";
PathEditor.props = ["isDebugMode", "readonly", "resModel", "path", "update"];

// مكونات الإدخال الفرعية
class Input extends Component {}
Input.template = "advanced_web_domain_widget.DomainSelector.Input";
Input.props = ["value", "update"];

class Select extends Component {
    deserialize(value) { return JSON.parse(value); }
    serialize(value) { return JSON.stringify(value); }
}
Select.template = "advanced_web_domain_widget.DomainSelector.Select";
Select.props = ["value", "update", "options"];

// ============================================================================
// منطق معالجة القيم (Value Parsers & Editors)
// ============================================================================

const parsers = registry.category("parsers");
function parseValue(fieldType, value) {
    const parser = parsers.get(fieldType, (value) => value);
    try { return parser(value); } catch { return value; }
}

function makeEditor(component, { props, isSupported, defaultValue } = {}) {
    return {
        component,
        extractProps: props || (({ value, update }) => ({ value, update })),
        isSupported: isSupported || ((value) => !(value instanceof Expression)),
        defaultValue: defaultValue || ((fieldDef, operator) => {
            switch (operator) {
                case "in": case "not in": return [];
                case "set": case "not_set": return false;
                case "date_filter": return "today";
                default: {
                    let val = "";
                    if (fieldDef) {
                        if (["integer", "float", "monetary"].includes(fieldDef.type)) val = 1;
                        if (fieldDef.type === "boolean") val = false;
                    }
                    return operator === "between" ? [val, val] : val;
                }
            }
        }),
    };
}

// ----------------------------------------------------------------------------
// تعريفات الحقول التفصيلية (FIELD DESCRIPTIONS) - الـ 600 سطر بتوعك هنا
// ----------------------------------------------------------------------------

const DATETIME = {
    operators: ["=", "!=", ">", ">=", "<", "<=", "between", "set", "not_set", "date_filter"],
    editors: {
        default: makeEditor("DateTimeInput", {
            props: ({ value, update, fieldDef }) => ({
                value: fieldDef.type === 'date' ? deserializeDate(value) : deserializeDateTime(value),
                onApply: (val) => update(fieldDef.type === 'date' ? serializeDate(val) : serializeDateTime(val)),
            }),
        }),
        date_filter: makeEditor(DateSelectionBits),
        between: makeEditor("Range", {
            props: ({ value, update, fieldDef }) => ({
                value, update, fieldDef, editorInfo: getEditorInfo(fieldDef)
            })
        }),
    },
    defaultValue: (fieldDef) => {
        const now = moment();
        return fieldDef.type === 'date' ? serializeDate(now) : serializeDateTime(now);
    }
};

const RELATIONAL_EDITOR_IN = makeEditor(DomainSelectorAutocomplete, {
    props: ({ value, update, fieldDef }) => ({
        resModel: fieldDef.relation || "",
        fieldString: fieldDef.string,
        update: (resIds) => update([...new Set(resIds)]),
        resIds: Array.isArray(value) ? [...new Set(value)] : value,
    }),
});

const RELATIONAL_EDITOR_EQUALITY = makeEditor(DomainSelectorSingleAutocomplete, {
    props: ({ value, update, fieldDef }) => ({
        resModel: fieldDef.relation,
        fieldString: fieldDef.string,
        update, resId: value,
    }),
    isSupported: () => true,
});

export const FIELD_DESCRIPTIONS = {
    boolean: {
        operators: ["is", "is_not"],
        editors: { default: makeEditor(Select, {
            props: ({ value, update }) => ({ value, update, options: [[true, _t("set")], [false, _t("not set")]] })
        })},
        defaultValue: () => true
    },
    char: {
        operators: ["=", "!=", "ilike", "not ilike", "in", "not in", "set", "not_set"],
        editors: {
            default: makeEditor(Input),
            in: makeEditor("TagInput"),
            "not in": makeEditor("TagInput")
        },
        defaultValue: () => ""
    },
    date: DATETIME,
    datetime: DATETIME,
    integer: {
        operators: ["=", "!=", ">", ">=", "<", "<=", "between", "set", "not_set"],
        editors: {
            default: makeEditor(Input, {
                props: ({ value, update, fieldDef }) => ({ value: String(value), update: (v) => update(parseValue(fieldDef.type, v)) })
            }),
            between: makeEditor("Range")
        },
        defaultValue: () => 1
    },
    many2one: {
        operators: ["in", "not in", "=", "!=", "ilike", "not ilike", "set", "not_set"],
        editors: {
            "=": RELATIONAL_EDITOR_EQUALITY,
            "!=": RELATIONAL_EDITOR_EQUALITY,
            "in": RELATIONAL_EDITOR_IN,
            "not in": RELATIONAL_EDITOR_IN,
            "set": { component: null, isSupported: (v) => v === false },
            "not_set": { component: null, isSupported: (v) => v === false }
        },
        defaultValue: () => false
    },
    selection: {
        operators: ["=", "!=", "in", "not in", "set", "not_set"],
        editors: {
            default: makeEditor(Select, { props: ({ value, update, fieldDef }) => ({ value, update, options: fieldDef.selection || [] }) }),
            "in": makeEditor(Input, { props: ({ value, update }) => ({ value: formatAST(toPyValue(value)), update: (v) => update(evaluateExpr(v)) }) })
        },
        defaultValue: (f) => f.selection ? f.selection[0][0] : false
    },
    id: {
        operators: ["=", "!=", ">", ">=", "<", "<=", "between", "in", "not in"],
        editors: {
            default: makeEditor(Input),
            in: RELATIONAL_EDITOR_IN,
            "=": RELATIONAL_EDITOR_EQUALITY
        },
        defaultValue: () => 1
    }
};

// ----------------------------------------------------------------------------
// الدوال المساعدة (Helper Functions)
// ----------------------------------------------------------------------------

export function getFieldInfo(fieldDef) {
    const { type, name } = fieldDef || {};
    if (name === "id") return FIELD_DESCRIPTIONS.id;
    return FIELD_DESCRIPTIONS[type] || { operators: ["=", "!="], editors: { default: makeEditor(Input) }, defaultValue: () => "" };
}

export function getEditorInfo(fieldDef, operator) {
    const descr = getFieldInfo(fieldDef);
    const editorInfo = descr.editors[operator] || descr.editors.default;
    editorInfo.defaultValue = () => getDefaultValue(fieldDef, operator);
    return editorInfo;
}

export function getOperatorsInfo(fieldDef) {
    const descr = getFieldInfo(fieldDef);
    return selectOperators(descr.operators);
}

export function getDefaultValue(fieldDef, operator) {
    const descr = getFieldInfo(fieldDef);
    return descr.defaultValue(fieldDef, operator);
}

export function getDefaultOperator(fieldDef) {
    const descr = getFieldInfo(fieldDef);
    return descr.operators[0];
}