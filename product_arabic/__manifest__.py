# -*- coding: utf-8 -*-
######################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: MOHAMED ASHIQ KK (Contact : odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
########################################################################################

{
    'name': 'Arabic product name in POS Receipt',
    'version': '16.0.1.0.0',
    'summary': """Generates Arabic product names in POS receipts""",
    'description': """This module enables user to print the product names in Arabic language in POS receipts""",
    'author': "Cybrosys Techno Solutions",
    'company': 'Cybrosys Techno Solutions',
    'website': 'http://www.cybrosys.com',
    'maintainer': 'Cybrosys Techno Solutions',
    'category': 'Point of Sale',
    'depends': ['point_of_sale', 'product'],
    'data': [
        'views/product_arabic.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'product_arabic/static/src/js/db.js',
            'product_arabic/static/src/js/pos_receipt.js',
            'product_arabic/static/src/xml/pos_screen.xml',
        ],
    },
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'price': 9.99,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': False,
}
