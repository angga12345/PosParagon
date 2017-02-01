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
    "name": "PTI: Journal Entry Reverse and Duplicate",
    "version": "1.0",
    "author": "Port Cities",
    "website": "http://portcitiesindonesia.com",
    "category": "Custom",
    "depends": ["pti_stock_default_mto","pti_bank_statement","pti_branch","pti_additional_models"],
    "description": """
Modul Journal Entry Correction\n
version .1.0\n
======================\n
@SitiMawaddah
- add new button Cancel Entry on Journal entries\n
Functions :
- Unreconcile the initial transaction: Unreconcile each items in the entry
- Proceed the same function than button Reverse Entry.
- Reconcile the initial transaction with the reversal.
- Duplicate the transaction with error and change the partner with the one selected in the wizard. The new transaction (issue by duplication) is a draft and must be validated manually
""",
    "demo_xml":[],
    "data":[
        "wizard/account_move_correction_view.xml",
        "view/account_move.xml",
    ],
    "active": False,
    "installable": True,
}

