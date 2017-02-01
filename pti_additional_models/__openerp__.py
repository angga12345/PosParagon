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
    "name": "PTI: Additional models",
    "version": "1.0",
    "author": "Port Cities",
    "website": "http://portcitiesindonesia.com",
    "category": "Generic Modules",
    "depends": ["pti_branch"],
    "description": """
ALL new models add in this module
""",
    "demo_xml":[],
    "data":[
        "data/product_brand.xml",
        "data/product_uom.xml",
        "security/ir.model.access.csv",
        "view/additional_models_view.xml",
        "view/partner_group_menu.xml",
        "view/picking_sort_order.xml",
    ],
    "active": False,
    "installable": True,
    "auto_install": False
}

