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
    "name": "PTI: Stock Picking",
    "version": "1.0",
    "author": "Port Cities",
    "website": "http://portcitiesindonesia.com",
    "category": "Generic Modules",
    "depends": ["pti_do_report"],
    "description": """
Default Odoo:
1. when DO get correction from WH. Users need edit all product on DO.

2. when reverse product only 3-5. Users need to delete all product in wizard

New requests :

1. When corecttion DO:
        - add button "Finish Update". 
        - User only update several product then click that button.
        - Will update all product Done=To Do
2. Reverse flow :
        - Set wizard reverse with 0 product.
        - add button "Reverse All" use when reverse all products and fill automatic all product in wizard.
        
v1.0 by SM

3. Default partner in Picking if customer is consignment or TL (team leader)

v1.2 by bima

4. Several mark as todo in 1 click

v1.3 by Aziz


5. -add field boolean is_retur and is_have_account_cn in stock.picking
   -make button generate credit note invisible   
    when condition is "state != done" or "is_retur = False" or "is_have_account_cn = True"
by Reza Akbar

""",
    "demo_xml":[],
    "data":[
        'security/ir.model.access.csv',
        'wizard/stock_return_picking_view.xml',
        'wizard/stock_picking_act_wizard.xml',
        'views/stock_view.xml',
        'views/stock_cancel_DO_warning_view.xml',
    ],
    "active": False,
    "installable": True,
}

