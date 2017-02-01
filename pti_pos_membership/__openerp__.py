{
    'name': 'PTI-POS: Membership',
    'version': '1.0',
    'author': 'Port Cities',
    'description': """
v1.0
----
Application Membership
===============================
- membership discount based on product & based on category product (Global)

by Helmi A.P

    """,
    'website': 'http://portcitiesindonesia.com',
    'depends': ["point_of_sale", "account", "pti_additional_models"],
    'category': 'Module POS-Membership',
    'data': [
            "view/membership_view.xml",
            "data/member.types.csv",
             ],
    'qweb':  [
            
              ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
