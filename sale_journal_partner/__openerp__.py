{
    "name": "PTI: Sale Journal by Partner",
    "version": "1.2",
    "author": "Port Cities",
    "website": "http://portcitiesindonesia.com",
    "category": "Generic Modules",
    "depends": [
                "account",
                "stock",
                "pti_invoice_account"
                ],
    "description": """
v 1.0
- Add menu journal sequence and add button on form view to update sequence
- Add field on customer to select Sales Journal from account.journal
- If create invoice to fill journal_id based on partner setting
    by Akhmad Fauzi Herdiyansah
v 1.1
- Add Picking sequence depend on journal in partner
    by Muhammad Nizar
v 1.2
- Recorrect sequence for cancelliations invoice format
    by Muhammad Nizar
- Add sequence SO for Paragon and Parama customer is independent
    by Akhmad Fauzi Herdiyansah
""",
    "demo_xml":[],
    "data":[
            'data/data_config.xml',
            'view/journal.xml'
            ],
    "active": False,
    "installable": True,
    "application" : False,
}
