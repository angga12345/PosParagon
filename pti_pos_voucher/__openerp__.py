{
    'name': 'PTI-POS: Product voucher',
    'version': '1.0',
    'author': 'Port Cities',
    'description': """
v1.0
----
Application Product Voucher: make a product voucher
===============================
- have a menu to add product voucher
- filter only product voucher
- have a period start and end date on product voucher

by Helmi A.P

v1.1
----
Product Voucher on front end
===============================
- voucher only use once. After used, it will disappear from product_list


by AK

v1.2
----
Inactive Expired Product Voucher
================================
- check automaticaly product voucher that already expired and make into inactive

    """,
    'website': 'http://portcitiesindonesia.com',
    'depends': ["stock", "point_of_sale"],
    'category': 'Module POS-Voucher',
    'data': [
            "view/voucher_view.xml",
            "view/templates.xml",
            "view/security.xml",
            "data/ir_cron.xml",
             ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
