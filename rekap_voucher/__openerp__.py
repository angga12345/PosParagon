{
    'name': 'WBH Rekapitulasi Voucher Per Store',
    'category': 'account',
    'version': '1.0',
    'depends': ['base','stock','point_of_sale'],
    'author': 'Port Cities',
    'description': '''
   Sale Report: Template for WBH Rekap Voucher
   Author : Erba Lutfina \n
   v.1.1 \n
    change wizard, and include start to end period \n
    create excel report rekap_voucher\n
    author: Erba Lutfina
    ''',
    'data': [
#         'views/ba_view_report.xml',
        'wizard/rekap_voucher_view.xml',    
#         'action_report.xml', 
    ],
    'installable': True,
    'active': False,
    'auto_install': False
}