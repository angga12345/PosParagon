{
    'name': 'Point of Sale - Discount Based On Date',
    'version': '1.0.',
    'category': 'Point Of Sale',
    "author": "Port Cities",
    'description': """
    This module intends to filter discount based on date and time
    """,
    'depends': ['pti_pos_special_product_discount'],
    'data': [
        'views/pos_data.xml',
        'views/loyalty_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'website': 'https://www.portcities.net',
    'auto_install': False,
    "active": False
}
