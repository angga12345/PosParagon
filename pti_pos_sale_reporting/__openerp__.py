{
    'name': 'Sale Reporting',
    'version': '1.0',
    'sequence': 6,
    'summary': 'For each/all MDS Store',
    'description': """

=======================

This module contains Sale Reporting for POS Orders

""",
    'depends': ['base','point_of_sale', 'pti_pos_pricelist_discount'],
    'data': [
             'mds_report_menu.xml',
             'wizard/report_mds_all_total_sale_view.xml',
             'wizard/report_mds_all_category_view.xml',
             'wizard/report_mds_all_category_per_store_view.xml'
    ],
    'installable': True,
    'auto_install': False,
}
