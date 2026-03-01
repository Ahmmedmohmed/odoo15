/** @odoo-module **/

import { Domain } from "../domain";
import { getDefaultValue, getDefaultOperator } from "./domain_selector_fields";
import {
    Expression,
    toValue,
    toDomain,
    toTree,
    normalizeValue,
    formatValue as toSring,
} from "../domain_tree";
import { getOperatorInfo } from "./domain_selector_operators";

const { _t } = require('web.core');
const { unique, zip } = require('web.utils');

/**
 * تحويل المعاملات الحقيقية (=، !=) إلى معاملات واجهة (is, set, not_set)
 */
export function createVirtualOperators(tree, getFieldDef) {
    if (tree.type === "condition") {
        const { path, operator, value } = tree;
        if (["=", "!="].includes(operator)) {
            const fieldDef = getFieldDef(path);
            if (fieldDef && fieldDef.type === "boolean") {
                return Object.assign({}, tree, { operator: operator === "=" ? "is" : "is_not" });
            } else if (fieldDef && fieldDef.type !== "many2one" && value === false) {
                return Object.assign({}, tree, { operator: operator === "=" ? "not_set" : "set" });
            }
        }
        return tree;
    }
    const processedChildren = tree.children.map((c) => createVirtualOperators(c, getFieldDef));
    return Object.assign({}, tree, { children: processedChildren });
}

/**
 * إرجاع المعاملات الافتراضية إلى أصلها قبل إرسالها للسيرفر
 */
function removeVirtualOperators(tree) {
    if (tree.type === "condition") {
        const { operator } = tree;
        if (["is", "is_not"].includes(operator)) {
            return Object.assign({}, tree, { operator: operator === "is" ? "=" : "!=" });
        }
        if (["set", "not_set"].includes(operator)) {
            return Object.assign({}, tree, { operator: operator === "set" ? "!=" : "=" });
        }
        return tree;
    }
    const processedChildren = tree.children.map((c) => removeVirtualOperators(c));
    return Object.assign({}, tree, { children: processedChildren });
}

export function buildDomain(domainSelectorTree) {
    const tree = removeVirtualOperators(domainSelectorTree);
    return toDomain(tree);
}

export function buildDomainSelectorTree(domain, getFieldDef, options = {}) {
    const tree = toTree(domain, options);
    return createVirtualOperators(tree, getFieldDef);
}

export function cloneTree(tree) {
    const clone = {};
    for (const key in tree) {
        let value = tree[key];
        if (value instanceof Expression) {
            clone[key] = new Expression(value.toAST());
        } else if (Array.isArray(value)) {
            clone[key] = value.map(v => v);
        } else {
            clone[key] = value;
        }
    }
    return clone;
}

/**
 * تحويل السجل المختار إلى نص مفهوم (Label)
 */
function formatValueLabel(val, disambiguate, fieldDef, displayNames) {
    if (val instanceof Expression) return val.toString();

    if (displayNames && (Number.isInteger(val) && val >= 1)) {
        return displayNames[val] || sprintf(_t("Inaccessible ID: %s"), val);
    }

    if (fieldDef && fieldDef.type === "selection") {
        const option = (fieldDef.selection || []).find(([v]) => v === val);
        if (option) return option[1];
    }

    return disambiguate && typeof val === "string" ? JSON.stringify(val) : val;
}

export function leafToString(fieldDef, operatorInfo, value, displayNames) {
    const description = {
        operatorDescription: operatorInfo.label,
        valueDescription: null,
    };

    if (["set", "not_set"].includes(operatorInfo.operator)) return description;

    const values = (Array.isArray(value) ? value : [value]).map((val) =>
        formatValueLabel(val, false, fieldDef, displayNames)
    );

    let join = _t("or");
    if (operatorInfo.operator === "between") join = _t("and");
    if (["in", "not in"].includes(operatorInfo.operator)) join = ",";

    description.valueDescription = {
        values,
        join,
        addParenthesis: Array.isArray(value)
    };
    return description;
}

/**
 * تبسيط شجرة الـ Domain لدمج الشروط المتكررة على نفس الحقل
 */
export function simplifyTree(tree, isRoot = true) {
    if (tree.type === "condition") return tree;

    const processedChildren = tree.children.map((c) => simplifyTree(c, false));
    if (tree.value === "&") return Object.assign({}, tree, { children: processedChildren });

    const children = [];
    const childrenByPath = {};

    for (const child of processedChildren) {
        if (child.type === "condition" && ["=", "in"].includes(child.operator) && typeof child.path === "string") {
            if (!childrenByPath[child.path]) childrenByPath[child.path] = [];
            childrenByPath[child.path].push(child);
        } else {
            children.push(child);
        }
    }

    for (const path in childrenByPath) {
        if (childrenByPath[path].length === 1) {
            children.push(childrenByPath[path][0]);
        } else {
            const combinedValue = [];
            childrenByPath[path].forEach(c => {
                if (Array.isArray(c.value)) combinedValue.push(...c.value);
                else combinedValue.push(c.value);
            });
            children.push({
                type: "condition",
                negate: false,
                operator: "in",
                path: path,
                value: normalizeValue(combinedValue),
            });
        }
    }
    return (children.length === 1 && !isRoot) ? children[0] : Object.assign({}, tree, { children });
}

/**
 * جلب الوصف النصي الكامل للـ Domain ليظهر في Facets البحث
 */
export function useGetDomainTreeDescription() {
    const env = owl.Component.env;
    return async (resModel, tree) => {
        const simplified = simplifyTree(tree);
        const domainStr = buildDomain(simplified);

        // استدعاء الخدمات في أودو 15
        const fieldService = env.services.field;
        const nameService = env.services.name;

        const paths = new Domain(domainStr).ast.value
            .filter(n => [4, 10].includes(n.type))
            .map(n => toValue(n.value[0]));

        // جلب أسماء الحقول والمعلومات
        const fieldDefs = await fieldService.loadFields(resModel);

        // بناء الوصف النهائي (Simplified logic for Odoo 15)
        return domainStr; // أو يمكنك بناء النص التفصيلي هنا
    };
}