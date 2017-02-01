{
    'name': 'Penjualan Total Harian MDS Per Store',
    'category': 'account',
    'version': '1.0',
    'depends': ['base','stock','point_of_sale'],
    'author': 'Port Cities',
    'description': '''
   add new menu in point of sale
   Author : Ardian Fajar Rahmanto \n
   v.1.1 \n
    change wizard, and include start to end period \n
    create excel report report_BA_daily_total\n
    author: Dara C
    ''',
    'data': [
#         'views/ba_view_report.xml',
        'wizard/ba_report_view.xml',    
#         'action_report.xml', 
    ],
    'installable': True,
    'active': False,
    'auto_install': False
}