  {
    'name': 'PTI BA Account Restriction',
    'category': 'account',
    'version': '1.0',
    'depends': ['base','point_of_sale'],
    'author': 'Port Cities',
    'description': '''
   add BA Account Restriction :\n
   1. User with BA Account type cannot edit POS Orders (Point of Sale/Orders)
   2. In Point of Sale kanban view, hide the Setting button for every shop for user type BA
   \nAuthor : FLR
    ''',
    'data': [
        'views/ba_view_config.xml'
    ],
    'installable': True,
    'active': False,
    'auto_install': False
}
