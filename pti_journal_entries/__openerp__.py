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
    'name': 'PTI Journal Entries',
    'version': '1.0',
    'depends': ['pti_branch'],
    'author': 'Port Cities',
    'description': """
    - Make menu Adviser in Acocunting visible for group PTI Invoice.
    - Create rules for journal entries and journal items filter by DC.
    Author : PAA
    V.1.2
    - spesific account discount 
    Author : Portcities
    V.1.3
    - Make generate_credit_note from stock_picking if is_retur True
    by Reza Akbar
    """,
    'website': 'http://www.portcities.net',
    'category': 'Account',
    'sequence': 1,
    'data': ['account_view.xml',
             'security/account_rules.xml',
             'views/trial_balance_report.xml'],
    'auto_install': False,
    'installable': True,
    'application': False,
}

