{
    'name': 'Multiple Categories',
    'version': '1.0',
    'sequence': 6,
    'summary': 'For any multiple categories',
    'description': """

=======================

This module allows you to define a multiple category of product

""",
    'depends': ['sale', 'point_of_sale', 'pti_branch'],
    'data': [
        'view/product_view.xml',
        'view/pos_product_menu_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
