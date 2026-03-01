/** @odoo-module **/

// استيراد المكتبات بأسلوب متوافق مع Odoo 15
const { formatAST, toPyValue } = require("web.py_utils");
import { Domain } from "../domain";

/**
 * قاموس لعمليات النفي المنطقية للمعاملات
 */
const TERM_OPERATORS_NEGATION = {
    "<": ">=",
    ">": "<=",
    "<=": ">",
    ">=": "<",
    "=": "!=",
    "!=": "=",
    "in": "not in",
    "like": "not like",
    "ilike": "not ilike",
    "not in": "in",
    "not like": "like",
    "not ilike": "ilike",
};

/**
 * كلاس لتمثيل التعبيرات البرمجية (Expressions)
 */
export class Expression {
    constructor(ast) {
        this._ast = ast;
        this._expr = formatAST(ast);
    }

    toAST() {
        return this._ast;
    }

    toString() {
        return this._expr;
    }
}

// دالة لتنسيق القيم وتحويلها لنصوص
export function formatValue(value) {
    return formatAST(toAST(value));
}

// دالة لتنظيف القيم لضمان عدم وجود مصفوفات متداخلة
export function normalizeValue(value) {
    return toValue(toAST(value));
}

/**
 * تحويل الـ AST إلى قيمة برمجية مفهومة (Value)
 */
export function toValue(ast, isWithinArray = false) {
    if ([4, 10].includes(ast.type) && !isWithinArray) {
        /** 4: list, 10: tuple */
        return ast.value.map((v) => toValue(v, true));
    } else if ([0, 1, 2].includes(ast.type)) {
        /** 0: number, 1: string, 2: boolean */
        return ast.value;
    } else if (ast.type === 6 && ast.op === "-" && ast.right.type === 0) {
        /** 6: unary operator */
        return -ast.right.value;
    } else if (ast.type === 5 && ["false", "true"].includes(ast.value)) {
        /** 5: name */
        return JSON.parse(ast.value);
    } else {
        return new Expression(ast);
    }
}

/**
 * تحويل القيمة البرمجية إلى AST (Abstract Syntax Tree)
 */
export function toAST(value) {
    if (value instanceof Expression) {
        return value.toAST();
    }
    if (Array.isArray(value)) {
        return { type: 4, value: value.map(toAST) };
    }
    return toPyValue(value);
}

// ============================================================================
// منطق بناء الشجرة (Tree Construction Logic)
// ============================================================================



function _construcTree(ASTs, distributeNot, negate = false) {
    const [firstAST, ...tailASTs] = ASTs;

    if (firstAST.type === 1 && firstAST.value === "!") {
        return _construcTree(tailASTs, distributeNot, !negate);
    }

    const tree = { type: firstAST.type === 1 ? "connector" : "condition" };
    if (tree.type === "connector") {
        tree.value = firstAST.value;
        if (distributeNot && negate) {
            tree.value = tree.value === "&" ? "|" : "&";
            tree.negate = false;
        } else {
            tree.negate = negate;
        }
        tree.children = [];
    } else {
        const [pathAST, operatorAST, valueAST] = firstAST.value;
        tree.path = toValue(pathAST);
        const operator = toValue(operatorAST);
        if (negate && typeof operator === "string" && TERM_OPERATORS_NEGATION[operator]) {
            tree.operator = TERM_OPERATORS_NEGATION[operator];
            tree.negate = false;
        } else {
            tree.operator = operator;
            tree.negate = negate;
        }
        tree.value = toValue(valueAST);
    }

    let remaimingASTs = tailASTs;
    if (tree.type === "connector") {
        for (let i = 0; i < 2; i++) {
            const { tree: child, remaimingASTs: otherASTs } = _construcTree(
                remaimingASTs,
                distributeNot,
                distributeNot && negate
            );
            remaimingASTs = otherASTs;
            // دمج الموصلات المتشابهة (Flattening) لتبسيط الواجهة
            if (child.type === "connector" && !child.negate && child.value === tree.value) {
                tree.children.push(...child.children);
            } else {
                tree.children.push(child);
            }
        }
    }
    return { tree, remaimingASTs };
}

export function construcTree(initialASTs, options = {}) {
    const value = options.defaultConnector || "&";
    if (!initialASTs.length) {
        return { type: "connector", value, negate: false, children: [] };
    }
    const { tree } = _construcTree(initialASTs, !!options.distributeNot);
    if (tree.type === "condition") {
        return { type: "connector", value, negate: false, children: [tree] };
    }
    return tree;
}

/**
 * تحويل الشجرة البرمجية إلى مصفوفة AST لإنتاج الـ Domain النهائي
 */
function getASTs(tree) {
    const ASTs = [];
    if (tree.type === "condition") {
        if (tree.negate) {
            ASTs.push(toAST("!"));
        }
        ASTs.push({
            type: 10,
            value: [tree.path, tree.operator, tree.value].map(toAST),
        });
        return ASTs;
    }

    const length = tree.children.length;
    if (length && tree.negate) {
        ASTs.push(toAST("!"));
    }
    for (let i = 0; i < length - 1; i++) {
        ASTs.push(toAST(tree.value));
    }
    for (const child of tree.children) {
        ASTs.push(...getASTs(child));
    }
    return ASTs;
}

/**
 * دمج معاملات المقارنة المتتالية في معامل "between" الافتراضي
 */
export function createBetweenOperators(tree, isRoot = true) {
    if (tree.type === "condition") return tree;
    const processedChildren = tree.children.map((c) => createBetweenOperators(c, false));
    if (tree.value === "|") return Object.assign({}, tree, { children: processedChildren });

    const children = [];
    for (let i = 0; i < processedChildren.length; i++) {
        const child1 = processedChildren[i];
        const child2 = processedChildren[i + 1];
        if (
            child1.type === "condition" &&
            child2 &&
            child2.type === "condition" &&
            formatValue(child1.path) === formatValue(child2.path) &&
            child1.operator === ">=" &&
            child2.operator === "<="
        ) {
            children.push({
                type: "condition",
                negate: false,
                path: child1.path,
                operator: "between",
                value: normalizeValue([child1.value, child2.value]),
            });
            i += 1;
        } else {
            children.push(child1);
        }
    }
    return (children.length === 1 && !isRoot) ? children[0] : Object.assign({}, tree, { children });
}

/**
 * تفكيك معامل "between" الافتراضي إلى معاملات >= و <= الأصلية قبل الحفظ
 */
export function removeBetweenOperators(tree) {
    if (tree.type === "condition") {
        if (tree.operator !== "between") return tree;
        const { negate, path, value } = tree;
        return {
            type: "connector",
            negate,
            value: "&",
            children: [
                { type: "condition", negate: false, path, operator: ">=", value: value[0] },
                { type: "condition", negate: false, path, operator: "<=", value: value[1] },
            ],
        };
    }
    const processedChildren = tree.children.map((c) => removeBetweenOperators(c));
    const children = [];
    for (let i = 0; i < processedChildren.length; i++) {
        const child = processedChildren[i];
        if (child.type === "connector" && !child.negate && child.value === "&") {
            children.push(...child.children);
        } else {
            children.push(child);
        }
    }
    return Object.assign({}, tree, { children });
}

export function toDomain(tree) {
    const simplifiedTree = removeBetweenOperators(tree);
    const domainAST = { type: 4, value: getASTs(simplifiedTree) };
    return formatAST(domainAST);
}

export function toTree(domain, options = {}) {
    domain = new Domain(domain);
    const tree = construcTree(domain.ast.value, options);
    return createBetweenOperators(tree);
}