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
    "name": "PTI: Invoice",
    "version": "1.0",
    "author": "Port Cities",
    "website": "http://portcitiesindonesia.com",
    "category": "Invoice custom",
    "depends": ["pti_additional_models"],
    "description": """
Modul Invoices\n
version .1.0\n
======================\n
- add invoice.line qty_returned and discount_m2m\n
- change logic total to pay based on return product if exist\n
version .1.1\n
======================\n
@bima
v1.2\n
====\n
Add Different Sequence Invoice base on type code invoice (10 digit number invoice):\n
Reference :\n
- number 1 until 2 is represent last digit of year the manufacture invoices\n
- number 3 until 4 is represent type code of invoices\n
- number 5 until 10 is represent sequence number of invoices\n
invoices code :\n
-10 = Normal Sales\n
-20 = Consignment Sales\n
-30 = Debit Note\n
-40 = Credit Note\n
Example : 1610000001\n
@HelmiAP\n
""",
    "demo_xml":[],
    "data":[
        "security/ir.model.access.csv",
        "data/invoice_number_data.xml",
        "wizard/confirm_validation.xml",
        "wizard/credit_note_wizard.xml",
        "wizard/account_invoice_refund.xml",
        "view/credit_note.xml",
        "view/cancelation_invoice_view.xml",
        "view/debit_note.xml",
        "view/account_invoice_view.xml",
        "view/account_move.xml",
        "report/account_invoice_report.xml",
    ],
    "active": False,
    "installable": True,
}

