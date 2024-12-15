odoo.define('product_arabic.pos_receipt', function (require) {
"use strict";


var { Orderline } = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');


const ProductArabic = (Orderline) => class ProductArabic extends Orderline {
    export_for_printing() {
        var line = super.export_for_printing(...arguments);
        line.product_name_arabic = this.get_product().product_arabic;
        return line;
    }
}
Registries.Model.extend(Orderline, ProductArabic);
});
