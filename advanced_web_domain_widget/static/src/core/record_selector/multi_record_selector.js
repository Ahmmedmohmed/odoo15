/** @odoo-module **/

const { Component, onWillStart, onWillUpdateProps } = owl;
const { _t } = require('web.core');

// استيراد المكونات التابعة (تأكد من وجودها في المجلد أو تحويلها أيضاً)
import { RecordAutocomplete } from "./record_autocomplete";

export class MultiRecordSelector extends Component {
    setup() {
        // في أودو 15 نصل لخدمة الأسماء عبر البيئة (env)
        this.nameService = this.env.services.name;

        onWillStart(async () => {
            await this.computeDerivedParams();
        });

        onWillUpdateProps(async (nextProps) => {
            await this.computeDerivedParams(nextProps);
        });
    }

    async computeDerivedParams(props = this.props) {
        const displayNames = await this.getDisplayNames(props);
        this.tags = this.getTags(props, displayNames);
    }

    async getDisplayNames(props) {
        const ids = this.getIds(props);
        if (ids.length === 0) return {};
        return this.nameService.loadDisplayNames(props.resModel, ids);
    }

    getIds(props = this.props) {
        return props.resIds || [];
    }

    getTags(props, displayNames) {
        return (props.resIds || []).map((id, index) => {
            const text = (displayNames && typeof displayNames[id] === "string")
                ? displayNames[id]
                : _t("Inaccessible/missing record ID: %s").replace('%s', id);

            return {
                id: id,
                text: text,
                onDelete: () => {
                    const newIds = [
                        ...this.props.resIds.slice(0, index),
                        ...this.props.resIds.slice(index + 1),
                    ];
                    this.props.update(newIds);
                },
            };
        });
    }

    update(resIds) {
        // دمج السجلات الجديدة مع الموجودة سابقاً
        const currentIds = this.props.resIds || [];
        this.props.update([...currentIds, ...resIds]);
    }
}

// تعريف القالب والمكونات لـ OWL 1
MultiRecordSelector.template = "web.MultiRecordSelector";
MultiRecordSelector.components = {
    RecordAutocomplete,
    // ملاحظة: TagsList في أودو 15 قد تحتاج لاستدعائها من Registry أو تعريفها يدوياً
};

// تعريف الـ Props بأسلوب Odoo 15
MultiRecordSelector.props = {
    resIds: { type: Array },
    resModel: String,
    update: Function,
    domain: { type: Array, optional: true },
    context: { type: Object, optional: true },
    fieldString: { type: String, optional: true },
};