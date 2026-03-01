/** @odoo-module **/

// في أودو 15 نصل لـ Component من مكتبة owl العالمية
const { Component } = owl;

export class DateSelectionBits extends Component {
    /**
     * دالة التجهيز (Setup)
     * في OWL 1، يتم استدعاء constructor أو الـ Hooks المتاحة
     */
    setup() {
        // التحقق إذا كانت القيمة تمرر كتاريخ حقيقي (String Date)
        // وتحويلها إلى القيمة الافتراضية "today" ليتناسب مع منطق الموديول
        if (this.props.value && !isNaN(new Date(this.props.value))) {
            this.props.update("today");
        }
    }

    /**
     * معالجة تغيير القيمة من القائمة المنسدلة
     * @param {Event} ev
     */
    onchange(ev) {
        const newValue = ev.target.value;
        this.props.update(newValue);
    }
}

// ربط المكون بالقالب (Template)
DateSelectionBits.template = "advanced_web_domain_widget.DateSelectionBits";

// تعريف الـ Props لضمان التحقق من البيانات في OWL 1
DateSelectionBits.props = {
    value: { type: String },
    update: { type: Function },
};