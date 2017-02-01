{
    "name": "Sales Order Parama",
    "version": "1.2",
    "author": "Port Cities",
    "website": "http://portcitiesindonesia.com",
    "category": "Generic Modules",
    "depends": [
                "sale",
                "stock"
                ],
    "description": """
v 1.0
- update function write in SO, user can not edit if sale journal in partner = "Sales Paragon" and context 'PRM' in name SO. 
  And user can not edit if sale journal in partner = "Sales Parama" and context 'PRM' not in name SO
    by Ahmad Fauzi Herdiyansah
""",
    "demo_xml":[],
    "data":["data/data_config.xml"],
    "active": False,
    "installable": True,
    "application" : False,
}
