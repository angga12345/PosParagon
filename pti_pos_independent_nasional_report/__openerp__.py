{
    'name': 'Independent Nasional Store report',
    'category': 'account',
    'version': '1.0',
    'depends': ['base','stock','point_of_sale'],
    'author': 'Port Cities',
    'description': '''
   add Independent Nasional Store report 
   Author : Helmi A.P \n
    ''',
    'data': [
        'wizard/produk.xml',
        'wizard/penj_total_harian_mingguan_bulanan.xml', 
        'wizard/lap_penj_promo_disc.xml',
        'wizard/rekap_voucher.xml',
        'wizard/rekap_penjualan_bulanan.xml',
        'wizard/lap_penj_per_kategori.xml',    
    ],
    'installable': True,
    'active': False,
    'auto_install': False
}
