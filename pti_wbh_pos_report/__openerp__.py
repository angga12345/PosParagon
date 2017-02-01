{
    'name': 'WBH Pos Report',
    'category': 'account',
    'version': '1.0',
    'depends': ['base','stock', 'point_of_sale', 'pti_pos_pricelist_discount', 'pti_pos_sale_reporting'],
    'author': 'Port Cities',
    'description': '''
   add new menu in point of sale, and create report xls for this menu \n
   Author : Nisfari \n
    ''',
    'data': [
        'wizard/pti_wbh_pos_report_view.xml',  
        'wizard/lap_penj_per_kategori_view.xml',
        'wizard/lap_penj_per_kategori_nasional_view.xml'    
    ],
    'installable': True,
    'active': False,
    'auto_install': False
}