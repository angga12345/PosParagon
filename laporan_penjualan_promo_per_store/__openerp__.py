{
    'name': 'Laporan Penjualan Promo Per Store',
    'category': 'account',
    'version': '1.0',
    'depends': ['base','stock','point_of_sale'],
    'author': 'Port Cities',
    'description': '''
   Sale Report: Template for Laporan Penj. Promo per Store Detail
   Author : Nurul Anisa Sri Winarsih \n
   v.1.0 \n
    change wizard, include start to end period and store name\n
    create excel report penjualan_promo\n
    author: Nurul Anisa Sri Winarsih
    ''',
    'data': [
        'wizard/penjualan_promo_per_store_view.xml',    
    ],
    'installable': True,
    'active': False,
    'auto_install': False
}