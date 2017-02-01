{
    'name': 'Laporan Promo Discount',
    'category': 'account',
    'version': '1.0',
    'depends': ['base','stock','point_of_sale'],
    'author': 'Port Cities',
    'description': '''
   Sale Report: Template for WBH Nasional Laporan Penj. Promo Discount
   Author : Erba Lutfina \n
   v.1.1 \n
    change wizard, and include start to end period \n
    create excel report penjualan_item_qty\n
    author: Erba Lutfina
    ''',
    'data': [
#         'views/ba_view_report.xml',
        'wizard/penjualan_promo_discount_view.xml',    
#         'action_report.xml', 
    ],
    'installable': True,
    'active': False,
    'auto_install': False
}