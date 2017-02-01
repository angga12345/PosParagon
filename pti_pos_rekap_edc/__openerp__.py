{
    'name': 'Report Rekap EDC WBH Nasional and WBH Per Store',
    'category': 'account',
    'version': '1.0',
    'depends': ['base','stock', 'point_of_sale'],
    'author': 'Port Cities',
    'description': '''
    v.1.0 \n
    
   add new menu in point of sale and design excel report\n
   author: Feliks Wida \n
    ''',
    'data': [
        'wizard/rekap_edc_wbh_nasional_view.xml',
        'wizard/rekap_edc_wbh_per_store_view.xml',   
    ],
    'installable': True,
    'active': False,
    'auto_install': False
}
