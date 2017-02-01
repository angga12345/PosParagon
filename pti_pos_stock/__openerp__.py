{
    'name': 'PTI-POS: Current Stock Report',
    'version': '1.0',
    'author': 'Port Cities',
    'description': """
    v1.0

    Current Stock Report

    Author: Helmy A.P
    """,
    'website': 'http://portcitiesindonesia.com',
    'depends': ["pti_pos_pricelist_discount"],
    'category': 'POS Modules',
    'data': [
            'report_menu.xml',
            'view/current_stock_report_view.xml',
            'wizard/current_stock_report_wizard_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
