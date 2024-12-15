# -*- coding: utf-8 -*-
{
    'name': "POS Product Quantity Limit",
    'version': '16.0',
    'summary': """Product Quantity Limit in Point of Sale and invoice""",
    "category": 'Warehouse,Point of Sale',
    'description': """Module adds functionality to Limit Product Quantity in Point of Sale and invoice.""",
    'author': 'Neoteric Hub',
    'company': 'Neoteric Hub',
    'live_test_url': '',
    'price': 0,
    'currency': 'USD',
    'website': 'https://www.neoterichub.com',
    'depends': ['stock', 'point_of_sale'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/product_product_views.xml',
    ],
    'assets': {
        'web.assets_backend': [

        ],
        'point_of_sale.assets': [
            '/nthub_pos_product_quantity_limit/static/src/xml/RestrictQuantityPopup.xml',
            '/nthub_pos_product_quantity_limit/static/src/js/RestrictQuantityPopup.js',
            '/nthub_pos_product_quantity_limit/static/src/js/ProductScreen.js',
        ],
    },
    'images': ['static/description/banner.gif'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
