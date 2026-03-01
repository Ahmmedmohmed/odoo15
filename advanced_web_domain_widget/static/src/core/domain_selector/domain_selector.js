/** @odoo-module **/

import {
  buildDomain,
  buildDomainSelectorTree,
  cloneTree,
  extractIdsFromDomain,
  extractPathsFromDomain,
  leafToString,
  useGetDefaultLeafDomain,
  useLoadDisplayNames,
} from "./utils"; // تأكد من تحديث المسار
import { Domain } from "../domain";
import { CheckBox } from "@web/core/checkbox/checkbox";
import {
  getOperatorInfo,
  toOperator,
} from "./domain_selector_operators";
import {
  Editor,
  PathEditor,
  getDefaultOperator,
  getDefaultValue,
  getOperatorsInfo,
  getEditorInfo,
} from "./domain_selector_fields";
import { ModelFieldSelector } from "@web/core/model_field_selector/model_field_selector";
import { useLoadFieldInfo } from "@web/core/model_field_selector/utils";
import { formatValue } from "../domain_tree";

const { Component, onWillStart, onWillUpdateProps } = owl;
const { useState } = owl.hooks;

export class DomainSelector extends Component {
  setup() {
    // استدعاء الخدمات بأسلوب Odoo 15
    this.getDefaultLeafDomain = useGetDefaultLeafDomain();
    this.loadDisplayNames = useLoadDisplayNames();
    this.fieldService = this.env.services.field; // تغيير من useService
    this.loadFieldInfo = useLoadFieldInfo(this.fieldService);

    this.tree = null;
    this.includeArchived = false;
    this.archivedConnector = {
      type: "condition",
      value: [true, false],
      negate: false,
      path: "active",
      operator: "in",
    };

    onWillStart(async () => {
      await this.onPropsUpdated(this.props);
    });

    onWillUpdateProps(async (nextProps) => {
      await this.onPropsUpdated(nextProps);
    });
  }

  // ... (بقية الدوال البرمجية مثل notifyChanges و updatePath تبقى كما هي لأنها منطق برمجي بحت)

  async loadFieldDefs(resModel, paths) {
    const promises = [];
    const fieldDefs = {};
    for (const path of paths) {
      if (typeof path === "string") {
        promises.push(
          this.loadFieldInfo(resModel, path).then(({ fieldDef }) => {
            fieldDefs[path] = fieldDef;
          })
        );
      }
    }
    await Promise.all(promises);
    this.fieldDefs = fieldDefs;
  }
}

DomainSelector.template = "advanced_web_domain_widget._DomainSelector";
DomainSelector.components = {
  ModelFieldSelector,
  Editor,
  PathEditor,
  CheckBox,
};

// تعريف الـ Props بأسلوب أودو 15
DomainSelector.props = {
    domain: String,
    resModel: String,
    className: { type: String, optional: true },
    isDebugMode: { type: Boolean, optional: true },
    readonly: { type: Boolean, optional: true },
    update: { type: Function, optional: true },
};