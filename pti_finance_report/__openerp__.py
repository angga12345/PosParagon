{
    'name': 'Finance Report',
    'category': 'account',
    'version': '1.0',
    'depends': ['base','point_of_sale'],
    'author': 'Port Cities',
    'description': '''
   add new menu item for finance report
   Author : Fachrian Luthfi R & Ardian F.R\n
   v.1.1 \n
    Finance_Report \n
    ''',
    'data': [
        'wizard/lap_pengiriman_barang_view.xml',
        'wizard/lap_retur_view.xml',
        'wizard/lap_penjualan_view.xml',
        'wizard/lap_data_stok_view.xml',
        'wizard/lap_selisih_persediaan_view.xml'
    ],
    'installable': True,
    'active': False,
    'auto_install': False
}
