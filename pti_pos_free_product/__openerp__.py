{
    'name': 'Point of Sale Free Product',
    'version': '1.0.',
    'category': 'Point Of Sale',
    "author": "Port Cities",
    'summary': '100% Discount for Free Product',
    'description': """
    This module intends to give 100% discount for Free Product
    """,
    'depends': ['pti_pos_pricelist_discount','pti_pos_special_product_discount', 'point_of_sale'],
    'data': [
        'views/pos_data.xml',
        'views/loyalty.xml',
        'views/special_price_view.xml',
        'views/pos_order_view.xml',
        'views/product_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
        'static/src/xml/receipt.xml',
    ],
    'installable': True,
    'application': True,
    'website': 'https://www.portcities.net',
    'auto_install': False,
    "active": False
}
