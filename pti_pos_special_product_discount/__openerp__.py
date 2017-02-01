{
    'name': 'Special Discount Configuration',
    'version': '1.0',
    'category': 'pos',
    'description': """
v1.0
----
Application Special Discount Configuration
==========================================
This module to manage special discount product with loyalty programs.

by Adham HK
v1.1
----
- Once per reward when a Discount is active or applied

by Helmy A.P
    """,
    'author': 'Port Cities',
    'website': "http://www.idealisconsulting.com/",
    'depends': [
        "pti_pos_pricelist_discount",
    ],
    'data': [
        'views/loyalty_program_view.xml',
        'security/ir.model.access.csv',
        'views/pricelists_view.xml',
        'views/point_of_sale_view.xml',
        'views/templates.xml',
        'data/product.xml',
    ],
    'qweb': [
        'static/src/xml/loyalty.xml',
        'static/src/xml/template.xml',
        'static/src/xml/pos_config_view.xml',
#         'static/src/xml/pricelist_template.xml',
    ],
    'installable': True,
    'active': False,
}
