/** @odoo-module **/

const { Component, useRef } = owl;
const { useState } = owl.hooks;
const { _t } = require('web.core');

// استيراد المكونات المحلية والتبعية
import { Dialog } from "@web/core/dialog/dialog";
import { Domain } from "../domain";
import { DomainSelector } from "../domain_selector/domain_selector";

export class DomainSelectorDialog extends Component {
    setup() {
        // في أودو 15 نصل للخدمات عبر this.env.services
        this.notification = this.env.services.notification;
        this.rpc = this.env.services.rpc;
        this.user = this.env.services.user;

        this.state = useState({
            domain: this.props.domain
        });

        this.confirmButtonRef = useRef("confirm");
    }

    get confirmButtonText() {
        return this.props.confirmButtonText || _t("Confirm");
    }

    get dialogTitle() {
        return this.props.title || _t("Domain Selector");
    }

    get disabled() {
        if (this.props.disableConfirmButton) {
            return this.props.disableConfirmButton(this.state.domain);
        }
        return false;
    }

    get discardButtonText() {
        return this.props.discardButtonText || _t("Discard");
    }

    get domainSelectorProps() {
        return {
            className: this.props.className,
            resModel: this.props.resModel,
            readonly: this.props.readonly,
            isDebugMode: this.props.isDebugMode,
            defaultConnector: this.props.defaultConnector,
            defaultLeafValue: this.props.defaultLeafValue,
            domain: this.state.domain,
            update: (domain) => {
                this.state.domain = domain;
            },
        };
    }

    async onConfirm() {
        // تعطيل الزر لمنع الضغط المتكرر
        if (this.confirmButtonRef.el) {
            this.confirmButtonRef.el.disabled = true;
        }

        let domain;
        let isValid = true;

        try {
            // تجهيز الـ Context للتقييم (Evaluation)
            const evalContext = Object.assign({}, this.user.context, this.props.context);
            domain = new Domain(this.state.domain).toList(evalContext);

            // التحقق من صحة الـ Domain عبر السيرفر
            isValid = await this.rpc({
                route: "/web/domain/validate",
                params: {
                    model: this.props.resModel,
                    domain: domain,
                },
            });
        } catch (e) {
            isValid = false;
        }

        if (!isValid) {
            if (this.confirmButtonRef.el) {
                this.confirmButtonRef.el.disabled = false;
            }
            this.notification.add(_t("The domain is invalid. Please check the syntax."), {
                type: "danger",
            });
            return;
        }

        // إذا كان سليماً، نقوم بتنفيذ دالة التأكيد وإغلاق النافذة
        this.props.onConfirm(this.state.domain);
        this.props.close();
    }

    onDiscard() {
        this.props.close();
    }
}

// تعريف القالب والمكونات التابعة لـ OWL 1
DomainSelectorDialog.template = "advanced_web_domain_widget.DomainSelectorDialog";
DomainSelectorDialog.components = {
    Dialog,
    DomainSelector,
};

// تعريف الـ Props بأسلوب أودو 15
DomainSelectorDialog.props = {
    close: Function,
    onConfirm: Function,
    resModel: String,
    domain: String,
    className: { type: String, optional: true },
    defaultConnector: { type: String, optional: true },
    defaultLeafValue: { type: Array, optional: true },
    isDebugMode: { type: Boolean, optional: true },
    readonly: { type: Boolean, optional: true },
    text: { type: String, optional: true },
    confirmButtonText: { type: String, optional: true },
    disableConfirmButton: { type: Function, optional: true },
    discardButtonText: { type: String, optional: true },
    title: { type: String, optional: true },
    context: { type: Object, optional: true },
};

DomainSelectorDialog.defaultProps = {
    isDebugMode: false,
    readonly: false,
    context: {},
};