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
    'name': 'Money Collector',
    'category': 'account',
    'version': '1.0',
    'depends': ['base','sale','account','pti_branch','pti_invoice_account'],
    'author': 'Port Cities',
    'description': '''
* Add boolean Is COllector on CUstomers (partner)
* Create new menu Money COllector inside Sales Menu
* Create new menu Unpaid Invoice inside Sales Menu
    
    (Add new wizard,
     add button in tree view money collector that can show wizard
     add field in wizard
     add action button in wizard that can save in tree view
     by reza akbar portcities
''',
    'data': [
        'security/ir.model.access.csv',
        'wizard/collector_bonus_report_view.xml',
	'wizard/assign_collector.xml',
        'views/account_move_line_view.xml',
        'views/account_invoice_view.xml',
        "views/partner_view.xml",
    ],
    'installable': True,
    'active': False,
    'auto_install': False
}

