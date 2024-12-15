{
    'name': 'Custom Total Amount Paid from POS Orders',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Adds a column for the total amount paid by customers from POS orders',
    'description': 'This module adds a column in the list view to show the total amount paid by each customer from POS orders.',
    'author': 'Your Name',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
}
