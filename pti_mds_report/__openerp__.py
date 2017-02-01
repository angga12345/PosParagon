{
    'name': 'Laporan Penjualan Per Transaksi MDS Per Store',
    'category': 'account',
    'version': '1.0',
    'depends': ['base','stock', 'point_of_sale'],
    'author': 'Port Cities',
    'description': '''
    v.1.0 \n
    
   add new menu in point of sale and include start to end period create excel report\n
   author: Dara C \n
    ''',
    'data': [
        'wizard/mds_laporan_penjualan_view.xml',   
    ],
    'installable': True,
    'active': False,
    'auto_install': False
}
