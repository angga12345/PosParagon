{
    'name': 'PTI BA Account And Warning',
    'category': 'account',
    'version': '1.0',
    'depends': ['base','point_of_sale'],
    'author': 'Port Cities',
    'description': '''
   add BA Account Restriction :\n
   1. User with BA Account type cannot look button close in dashboard (Point of Sale/Orders)
   2. Create Warning when will close session
   \nAuthor : Ardian Fajar R.
    ''',
    'data': [
        'views/point_of_sale_js.xml'
    ],
    'installable': True,
    'active': False,
    'auto_install': False
}
