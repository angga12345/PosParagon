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
    "name": "PTI: Validation",
    "version": "1.1",
    "author": "Port Cities",
    "website": "http://portcitiesindonesia.com",
    "category": "Generic Modules",
    "depends": ["pti_branch"],
    "description": """
Application branch\n
==================\n
Installation:\n
1. Stock Adjustment by group user sales admin adjustment
2. Validate Stock Adjustment by group by finance user adjustment
3. Add "Product developer" group can create product with draft state and not sellable
4. Finance admin group validate the "draft" product in "request product" menuitem set product state to sellable 
@helmy\n 
v1.1\n
product validation :
1. Group prodev create product
2. Product able to sale after finance pusat validate product
@kresna \n
v.1.2\n
====\n
""",
    "demo_xml":[],
    "data":[
        "security/groups.xml",
        "security/ir.model.access.csv",
#         "view/stock_adjustment.xml",
        "view/product_validation.xml",
        "security/res.groups.csv",
    ],
    "active": False,
    "installable": True,
    "application" : True,
}

