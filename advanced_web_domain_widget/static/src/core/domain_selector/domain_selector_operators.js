/** @odoo-module **/

// في أودو 15، الترجمة وتنسيق النصوص يتم استيرادها من web.core
const { _t } = require('web.core');
const { sprintf } = require('web.core');
const { parseExpr } = require('web.py_utils');

import { formatValue, toValue } from "../domain_tree";

/**
 * @typedef {Object} OperatorInfo
 * @property {import("../domain_tree").Value} operator
 * @property {string} label
 * @property {number|"variable"} valueCount
 */

// تعريف مسميات المعاملات وعدد القيم التابعة لها
export const OPERATOR_DESCRIPTIONS = {
    "=": { label: "=", valueCount: 1 },
    "!=": { label: "!=", valueCount: 1 },
    "<=": { label: "<=", valueCount: 1 },
    "<": { label: "<", valueCount: 1 },
    ">": { label: ">", valueCount: 1 },
    ">=": { label: ">=", valueCount: 1 },
    "=?": { label: "=?", valueCount: 1 },
    "=like": { label: _t("=like"), valueCount: 1 },
    "=ilike": { label: _t("=ilike"), valueCount: 1 },
    like: { label: _t("like"), valueCount: 1 },
    "not like": { label: _t("not like"), valueCount: 1 },
    ilike: { label: _t("contains"), valueCount: 1 },
    "not ilike": { label: _t("does not contain"), valueCount: 1 },
    in: { label: _t("is in"), valueCount: "variable" },
    "not in": { label: _t("is not in"), valueCount: "variable" },
    child_of: { label: _t("child of"), valueCount: 1 },
    parent_of: { label: _t("parent of"), valueCount: 1 },

    // المعاملات الافتراضية (Virtual Operators) لسهولة الاستخدام
    is: { label: _t("is"), valueCount: 1 },
    is_not: { label: _t("is not"), valueCount: 1 },
    set: { label: _t("is set"), valueCount: 0 },
    not_set: { label: _t("is not set"), valueCount: 0 },
    date_filter: { label: _t("date filter"), valueCount: 1 },
    between: { label: _t("is between"), valueCount: 2 },
};

/**
 * تحويل المعامل إلى مفتاح نصي فريد للقائمة
 */
function toKey(operator, negate = false) {
    if (!negate && typeof operator === "string" && operator in OPERATOR_DESCRIPTIONS) {
        return operator;
    }
    return JSON.stringify([formatValue(operator), negate]);
}

/**
 * تحويل المفتاح المختار في القائمة إلى معامل برمجي (Odoo Operator)
 */
export function toOperator(key) {
    if (!key.includes("[")) {
        return [key, false];
    }
    const [expr, negate] = JSON.parse(key);
    return [toValue(parseExpr(expr)), negate];
}

/**
 * جلب معلومات المعامل (Label, Key, ValueCount)
 */
export function getOperatorInfo(operator, negate = false) {
    let operatorInfo;
    const key = toKey(operator, negate);

    if (typeof operator === "string" && operator in OPERATOR_DESCRIPTIONS) {
        const { label, valueCount } = OPERATOR_DESCRIPTIONS[operator];
        operatorInfo = {
            key,
            label: label.toString(),
            operator,
            negate,
            valueCount,
        };
    } else {
        operatorInfo = {
            key,
            label: formatValue(operator),
            operator,
            negate,
            valueCount: 0,
        };
    }

    if (negate) {
        // في أودو 15 نستخدم sprintf من web.core
        operatorInfo.label = sprintf(_t("not %s"), operatorInfo.label);
    }
    return operatorInfo;
}

/**
 * جلب قائمة كاملة من المعلومات لمجموعة من المعاملات
 */
export function selectOperators(operators) {
    return operators.map((operator) => getOperatorInfo(operator));
}