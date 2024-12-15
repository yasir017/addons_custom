/** @odoo-module **/

import { DomainSelectorBranchNodeBits } from "./domain_selector_branch_node";
import { DomainSelectorBranchOperatorBits } from "./domain_selector_branch_operator";
import { DomainSelectorLeafNodeBits } from "./domain_selector_leaf_node";

import { Component } from "@odoo/owl";

export class DomainSelectorRootNodeBits extends Component {
    get hasNode() {
        return this.props.node.operands.length > 0;
    }
    get node() {
        return this.props.node.operands[0];
    }

    insertNode(newNodeType) {
        this.props.node.insert(newNodeType);
    }

    onOperatorSelected(ev) {
        this.props.node.update(ev.detail.payload.operator);
    }
    onChange(ev) {
        this.props.node.update(ev.target.value, true);
        this.render();
    }
}
DomainSelectorRootNodeBits.template = "advanced_web_domain_widget.DomainSelectorRootNodeBits";
DomainSelectorRootNodeBits.components = {
    DomainSelectorBranchNodeBits,
    DomainSelectorBranchOperatorBits,
    DomainSelectorLeafNodeBits,
};
