# Copyright (C) 2016 by PT Paragon Technology And Innovation
#
# This file is part of PTI Odoo Addons.
#
# PTI Odoo Addons is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PTI Odoo Addons is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with PTI Odoo Addons.  If not, see <http://www.gnu.org/licenses/>.

{
    "name": "PTI: Branch",
    "version": "1.1",
    "author": "Port Cities",
    "website": "http://portcitiesindonesia.com",
    "category": "Generic Modules",
    "depends": ["sale_stock","pti_stock_report","account_accountant","account_cancel","pti_stock_default_mto","pti_bank_statement","pti_stock_report"],
    "description": """
Application branch\n
==================\n
Installation:\n
1. non active record rules see all leads (sale application)\n
2. non active record rules Personal Order and Personal Order Line\n
3. Check all default odoo 9 locations\n
@bima\n

v1.1\n
====\n
Add field Partner of DC and related Users. So, we can search DC by User Id\n
@SM\n
""",
    "demo_xml":[],
    "data":[
        "security/groups.xml",
        "security/kdc_user.xml",
        "security/finance_user.xml",
        "security/customer_order_user.xml",
        "security/delivery_order_user.xml",
        "security/invoicing_user.xml",
        "security/ir_rule.xml",
        "view/branch_view.xml",
        "view/filter_view.xml",
        "view/picking_shipment.xml",
        "security/ir.model.access.csv",
        "security/stock.location.csv",
        "security/ir.rule.csv",
        "security/res.groups.csv",
        "settings/settings.xml",
        "settings/company.xml",
        "settings/lang.xml",
        "settings/groups.xml",
        "wizard/customer_validation_view.xml"
    ],
    "active": False,
    "installable": True,
    "application" : True,
}

