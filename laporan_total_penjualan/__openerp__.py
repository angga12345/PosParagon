{
    'name': 'WBH Laporan Total Penjualan Per Store',
    'category': 'account',
    'version': '1.0',
    'depends': ['base','stock','point_of_sale'],
    'author': 'Port Cities',
    'description': '''
   Sale Report: Template for Laporan Total Penjualan
   Author : Nurul Anisa Sri Winarsih \n
   v.1.0 \n
    change wizard, include start to end period and store name\n
    create excel Report WBH Total Penjualan Per Store.xls\n
    author: Nurul Anisa Sri Winarsih
    ''',
    'data': [
        'wizard/laporan_total_penjualan_view.xml',    
    ],
    'installable': True,
    'active': False,
    'auto_install': False
}