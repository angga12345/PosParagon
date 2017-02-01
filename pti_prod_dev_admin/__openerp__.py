{
    'name': 'PTI prod development admin',
    'version': '1.0',
    'author': 'Port Cities',
    'website': 'http://portcitiesindonesia.com',
    'depends': ["base","pti_branch","stock"],
    
    'data': [
            
            "security/groups.xml",
            "views/sale_price_access.xml"
             ],
    

    'installable': True,
    'application': True,
    'auto_install': False,
}
