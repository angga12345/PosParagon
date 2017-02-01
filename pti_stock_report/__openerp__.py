{
    "name": "PTI: Stock Report",
    "version": "1.0",
    "author": "Port Cities",
    "website": "http://portcitiesindonesia.com",
    "category": "Generic Modules",
    "depends": ["base","stock"],
    "description": """
1. Stock adjustment report.\n
2. Quantity on hand report by location.\n
v1.0 by bima

""",
    "demo_xml":[],
    "data":[
        'views/action_report.xml',
        'views/tracking_picking_shipment_view.xml',
        'views/stock_adjustment_report.xml',
        'wizard/stock_picking_shipment_sequence.xml',
        'wizard/wizard_picking_shipment_view.xml',
        'wizard/qoh_report.xml',
        'report_stock_card.xml',
    ],
    "active": False,
    "installable": True,
}
