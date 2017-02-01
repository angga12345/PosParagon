{
    'name': 'PTI-POS: Pricelist & Discount',
    'version': '1.0',
    'author': 'Port Cities',
    'description': """
v1.0
----
Application Pricelist & Discount
===============================
-differs pricelist,discount,membership discount,promo for each shop to shop
-add restriction Group BA, Group Supervisor, Group Audit, Group Stock Taker, Group Finance
(BA can only see their region stores)

by Helmi A.P

v1.1
----
POS cashier frontend
===============================
-order cart validation (prod must be one type. have promo or havent).
-add batch number field in payment for payment type bank.

by Kresna

v1.2
----
POS [pay per piece , Disable button Price by user, Filter Product Brand based Brand Store]
==============================
-change +10, +20, +50 become +20K,+50K,+100K pay per piece
-can setting edit price (yes/not) just mark field allow edit price on the user setting tabs Point of sale
-filter Product Brand based Brand Store (when Store Brand Sale "wardah" display on the pos only show product "wardah" etc.)

by Helmi A.P

v1.3
----
POS [hidden button Guests and Customer on payment]

by Ardian, Fachrian

v1.4
----
POS [numpad only appear on stand alone shop]

by Helmi A.P

v1.5
----
POS [Show ID card, university, community fields from res partner in customer page of POS screen]

by zein

v1.6
----
POS [Domain filter Free Products in reward loyalty]

v1.7
----
POS [Copy SKU based on promo/non-promo]

by Zein

v1.8
----
- Add new field brand and category text
- Display the text in footer receipt backend

by Zein

v1.9
----
- Create Account Journal and Account Account Automatically when create pos config
by Reza Akbar

    """,
    'website': 'http://portcitiesindonesia.com',
    'depends': ["base","pti_additional_models","point_of_sale","stock","account","pos_loyalty","pos_restaurant","pti_product_brand", "pti_pos_membership"],
    'category': 'Module POS-Discount',
    'data': [
            #"settings/settings.xml",
            "data/sequence_list.xml",
            "data/pos_account_tags_data.xml",
            "security/groups.xml",
            "security/user_ba.xml",
            "security/res.groups.csv",
            "security/ir.model.access.csv",
            #"view/pos_data.xml",
            "static/src/xml/css_template.xml",
            "view/automatic_warehouse_view.xml",
            "view/templates.xml",
            "view/batch_number.xml",
            "view/kateg_shop.xml",
            "view/account_journal.xml",
            "view/account_bank_statement_line_view.xml",
            #"view/pos_data_js.xml"
            'view/pos_order_view.xml'
             ],
    'qweb':  [
            'static/src/xml/pos.xml',
            'static/src/xml/pos_resto_hidden_guests.xml',
            'static/src/xml/payment.xml',
            'static/src/xml/price_no_disc.xml',
#             'static/src/xml/account_bank_statement_line.xml'
              ],

    'installable': True,
    'application': True,
    'auto_install': False,
}