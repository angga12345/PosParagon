{
    'name': 'Laporan Penjualan Promo',
    'category': 'account',
    'version': '1.0',
    'depends': ['base','stock','pti_additional_models'],
    'author': 'Port Cities',
    'description': '''
   Sale Report: Template for Laporan Penj. Promo per Store
   Author : Nurul Anisa Sri Winarsih \n
   v.1.0 \n
    change wizard, and include start to end period \n
    create excel report penjualan_promo\n
    author: Nurul Anisa Sri Winarsih
    ''',
    'data': [
        'wizard/penjualan_promo_view.xml',    
    ],
    'installable': True,
    'active': False,
    'auto_install': False
}