/** @odoo-module **/
/*
 * This file is used to restrict out of stock product from ordering and show restrict popup
 */
import Registries from 'point_of_sale.Registries';
import ProductScreen from 'point_of_sale.ProductScreen';
import NumberBuffer from 'point_of_sale.NumberBuffer';

const RestrictProductQuantityScreen = (ProductScreen) => class RestrictProductQuantityScreen extends ProductScreen {
    async _clickProduct(event) {
        // Overriding product item click to restrict product out of stock
        const product = event.detail;
        var product_qty = this._product_order_quantity(this.currentOrder, product, 1) + 1;
        if (this.env.pos.config.product_quantity_limit && product.limit_quantity > 0 && product_qty > product.limit_quantity) {
            this.showPopup("RestrictQuantityPopup", {
                body: product.display_name + 'is Over the Quantity Limit equal ' + product.limit_quantity,
                pro_id: product.id
            });
            return;
        }
        if (this.env.pos.config.is_pos_bill_quantity_limit && this.env.pos.config.pos_bill_quantity_limit > 0 && this.currentOrder.selected_orderline ? this.currentOrder.selected_orderline.product.id !== product.id : true) {
            if(!this.currentOrder.orderlines.some(orderline => orderline.product.id === product.id)){
                var orderlines_length = this.currentOrder.orderlines.length;
                if (orderlines_length + 1 > this.env.pos.config.pos_bill_quantity_limit){
                    this.showPopup("RestrictQuantityPopup", {
                    body: 'Can not add more than '+ this.env.pos.config.pos_bill_quantity_limit +' Products',
                    pro_id: product.id
                    });
                    return;
                    }
                else {
                    await super._clickProduct(event)
                }
            }
            else {
                await super._clickProduct(event)
            }
        }
        else {
            await super._clickProduct(event)
        }
    }
    async _setValue(val) {
        var order_line = this.currentOrder.get_selected_orderline();
        var product = order_line ? order_line.product : null;
        if (order_line) {
            var product_qty = this._product_order_quantity(this.currentOrder, product, parseFloat(val))
            if (this.env.pos.numpadMode === 'quantity') {
//                if (this.env.pos.config.product_quantity_limit && product.limit_quantity > 0 && (parseFloat(val) > product.limit_quantity || product_qty + parseFloat(val) > product.limit_quantity)) {
                if (this.env.pos.config.product_quantity_limit && product.limit_quantity > 0 && (parseFloat(val) > product.limit_quantity || product_qty + parseFloat(val) > product.limit_quantity)) {
                    NumberBuffer.reset();
                    this.showPopup("RestrictQuantityPopup", {
                        body: product.display_name + 'is Over the Quantity Limit equal ' + product.limit_quantity,
                        pro_id: product.id
                    });
                }
                else {
                    await super._setValue(val);
                }
            }
            else {
                await super._setValue(val);
            }
        }
    }
    _product_order_quantity(currentOrder, product,val) {
        var sum_qty = 0
        for (let line of currentOrder.orderlines) {
            if (line.product.id == product.id) {
                sum_qty = sum_qty + line.quantity
            }
        }
        return val > 1 ? sum_qty - currentOrder.selected_orderline.quantity : sum_qty
    }
}
Registries.Component.extend(ProductScreen, RestrictProductQuantityScreen);
