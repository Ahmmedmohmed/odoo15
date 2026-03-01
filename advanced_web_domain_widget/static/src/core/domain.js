/** @odoo-module **/

// استيراد المكتبات بأسلوب متوافق مع Odoo 15
const { shallowEqual } = require("@web/core/utils/arrays");
const { evaluate, formatAST, parseExpr } = require("@web/core/py_js/py");
const { toPyValue } = require("@web/core/py_js/py_utils");

export class InvalidDomainError extends Error {}

/**
 * تمثيل الجافاسكريبت لـ Odoo Domain (متوافق مع نسخة 15)
 */
export class Domain {
    /**
     * دمج مصفوفة من الـ Domains باستخدام معامل معين (AND أو OR)
     */
    static combine(domains, operator) {
        if (domains.length === 0) {
            return new Domain([]);
        }
        const domain1 = domains[0] instanceof Domain ? domains[0] : new Domain(domains[0]);
        if (domains.length === 1) {
            return domain1;
        }
        const domain2 = Domain.combine(domains.slice(1), operator);
        const result = new Domain([]);
        const astValues1 = domain1.ast.value;
        const astValues2 = domain2.ast.value;
        const op = operator === "AND" ? "&" : "|";
        const combinedAST = { type: 4 /* List */, value: astValues1.concat(astValues2) };
        result.ast = normalizeDomainAST(combinedAST, op);
        return result;
    }

    static and(domains) {
        return Domain.combine(domains, "AND");
    }

    static or(domains) {
        return Domain.combine(domains, "OR");
    }

    static not(domain) {
        const result = new Domain(domain);
        result.ast.value.unshift({ type: 1, value: "!" });
        return result;
    }

    /**
     * تحييد بعض الحقول من الـ Domain (تستخدم في موديول Access Management)
     */
    static removeDomainLeaves(domain, keysToRemove) {
        function processLeaf(elements, idx, operatorCtx, newDomain) {
            const leaf = elements[idx];
            if (leaf.type === 10) {
                if (keysToRemove.includes(leaf.value[0].value)) {
                    if (operatorCtx === "&") {
                        newDomain.ast.value.push(...Domain.TRUE.ast.value);
                    } else if (operatorCtx === "|") {
                        newDomain.ast.value.push(...Domain.FALSE.ast.value);
                    }
                } else {
                    newDomain.ast.value.push(leaf);
                }
                return 1;
            } else if (leaf.type === 1) {
                if (
                    leaf.value === "|" &&
                    elements[idx + 1].type === 10 &&
                    elements[idx + 2].type === 10 &&
                    keysToRemove.includes(elements[idx + 1].value[0].value) &&
                    keysToRemove.includes(elements[idx + 2].value[0].value)
                ) {
                    newDomain.ast.value.push(...Domain.TRUE.ast.value);
                    return 3;
                }
                newDomain.ast.value.push(leaf);
                if (leaf.value === "!") {
                    return 1 + processLeaf(elements, idx + 1, "&", newDomain);
                }
                const firstLeafSkip = processLeaf(elements, idx + 1, leaf.value, newDomain);
                const secondLeafSkip = processLeaf(
                    elements,
                    idx + 1 + firstLeafSkip,
                    leaf.value,
                    newDomain
                );
                return 1 + firstLeafSkip + secondLeafSkip;
            }
            return 0;
        }

        domain = new Domain(domain);
        if (domain.ast.value.length === 0) {
            return domain;
        }
        const newDomain = new Domain([]);
        processLeaf(domain.ast.value, 0, "&", newDomain);
        return newDomain;
    }

    constructor(descr = []) {
        if (descr instanceof Domain) {
            return new Domain(descr.toString());
        } else {
            let rawAST;
            try {
                if (descr && descr.length) {
                    rawAST = typeof descr === "string" ? parseExpr(descr) : toAST(descr);
                } else {
                    rawAST = typeof descr === "string" ? parseExpr("[]") : toAST([]);
                }
            } catch (error) {
                throw new InvalidDomainError(`Invalid domain: ${descr}`, { cause: error });
            }
            this.ast = normalizeDomainAST(rawAST);
        }
    }

    contains(record) {
        const expr = evaluate(this.ast, record);
        return matchDomain(record, expr);
    }

    toString() {
        return formatAST(this.ast);
    }

    toList(context) {
        return evaluate(this.ast, context);
    }

    toJson() {
        try {
            const evaluatedAsList = this.toList({});
            const evaluatedDomain = new Domain(evaluatedAsList);
            if (evaluatedDomain.toString() === this.toString()) {
                return evaluatedAsList;
            }
            return this.toString();
        } catch {
            return this.toString();
        }
    }
}

export function evalDomain(modifier, evalContext) {
    if (modifier && typeof modifier !== "boolean") {
        modifier = new Domain(modifier).contains(evalContext);
    }
    return Boolean(modifier);
}

const TRUE_LEAF = [1, "=", 1];
const FALSE_LEAF = [0, "=", 1];
Domain.TRUE = new Domain([TRUE_LEAF]);
Domain.FALSE = new Domain([FALSE_LEAF]);

// --- الدوال المساعدة للتنقية والتحويل ---

function toAST(domain) {
    const elems = domain.map((elem) => {
        if (typeof elem === "string") {
            return { type: 1, value: elem };
        }
        return { type: 10, value: elem.map(toPyValue) };
    });
    return { type: 4, value: elems };
}

function normalizeDomainAST(domain, op = "&") {
    if (domain.type !== 4 && domain.type !== 10) {
        throw new InvalidDomainError("Invalid AST Type");
    }
    if (domain.value.length === 0) return domain;

    let expected = 1;
    for (const child of domain.value) {
        if (child.type === 1) {
            if (child.value === "&" || child.value === "|") expected++;
            else if (child.value !== "!") throw new InvalidDomainError("Unexpected String");
        } else if (child.type === 10 || child.type === 4) {
            if (child.value.length === 3) expected--;
        }
    }

    const values = domain.value.slice();
    while (expected < 0) {
        expected++;
        values.unshift({ type: 1, value: op });
    }
    return { type: 4, value: values };
}

function matchCondition(record, condition) {
    if (typeof condition === "boolean") return condition;
    const [field, operator, value] = condition;

    if (typeof field === "string" && field.includes(".")) {
        const names = field.split(".");
        return matchCondition(record[names[0]] || {}, [names.slice(1).join("."), operator, value]);
    }

    const fieldValue = typeof field === "number" ? field : record[field];

    switch (operator) {
        case "=": case "==": return shallowEqual(fieldValue, value);
        case "!=": case "<>": return !shallowEqual(fieldValue, value);
        case "<": return fieldValue < value;
        case "<=": return fieldValue <= value;
        case ">": return fieldValue > value;
        case ">=": return fieldValue >= value;
        case "in": return (Array.isArray(value) ? value : [value]).includes(fieldValue);
        case "not in": return !(Array.isArray(value) ? value : [value]).includes(fieldValue);
        case "ilike":
            return new RegExp(String(value).replace(/%/g, ".*"), "i").test(String(fieldValue));
        case "not ilike":
            return !new RegExp(String(value).replace(/%/g, ".*"), "i").test(String(fieldValue));
    }
    return true;
}

function matchDomain(record, domain) {
    if (domain.length === 0) return true;
    const reversed = Array.from(domain).reverse();
    const stack = [];

    for (const item of reversed) {
        if (item === "&" || item === "|") {
            const a = stack.pop();
            const b = stack.pop();
            stack.push(item === "&" ? (a && b) : (a || b));
        } else if (item === "!") {
            stack.push(!stack.pop());
        } else {
            stack.push(matchCondition(record, item));
        }
    }
    return stack.pop();
}