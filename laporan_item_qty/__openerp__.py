{
    'name': 'Laporan Penjualan Per Item',
    'category': 'account',
    'version': '1.0',
    'depends': ['base','stock','pti_additional_models'],
    'author': 'Port Cities',
    'description': '''
   Sale Report: Template for Laporan Penj. Per Item Qty per Store
   Author : Erba Lutfina \n
   v.1.1 \n
    change wizard, and include start to end period \n
    create excel report penjualan_item_qty\n
    author: Erba Lutfina
    ''',
    'data': [
#         'views/ba_view_report.xml',
        'wizard/penjualan_item_qty_view.xml',    
#         'action_report.xml', 
    ],
    'installable': True,
    'active': False,
    'auto_install': False
}