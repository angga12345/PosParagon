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
    "name": "PTI: Credit Limit",
    "version": "1.0",
    "author": "Indrajaya",
    "website": "http://www.pti-cosmetics.com",
    "category": "Custom",
    "depends": ["pti_customer_order"],
    "description": """
Adding credit limit for sale addons
""",
    "data": [
        "security/ir.model.access.csv",
        "wizard/confirm_box.xml",
        "res_partner_view.xml"
    ],
    "active": False,
    "installable": True,
    "auto_install": False
}

