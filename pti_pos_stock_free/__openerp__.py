{
    'name': 'PTI-POS: Current Stock Report Free Product',
    'version': '1.0',
    'author': 'Port Cities',
    'description': """
    v1.0

        Create another menu 'Current Stock Report Free Product'

        By Zein
    
    """,
    'website': 'http://portcitiesindonesia.com',
    'depends': ["pti_pos_pricelist_discount"],
    'category': 'POS Modules',
    'data': [
            'report_menu.xml',
            'view/current_stock_report_free_view.xml',
            'wizard/current_stock_report_free_wizard_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
