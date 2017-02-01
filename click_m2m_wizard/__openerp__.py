{
    'name': 'M2M Wizard',
    'version': '1.0',
    'depends': ["base","web","sale","pti_customer_order","account","purchase"],
    'author': 'Port Cities International',
    'description': """
v1.0
----
* Show wizard on many2many field click 
* Author : AK
    """,
    'website': 'http://www.portcitiesindonesia.com',
    'category': 'Web',
    'sequence': 1,
    'data': [
             'wizard/invoice_line_m2m_wizard.xml',
             'wizard/purchase_line_m2m_wizard.xml',
             'views/account_invoice.xml',
             'views/purchase.xml',
             ],
           
    'auto_install': False,
    'installable': True,
    'application': False,
}
