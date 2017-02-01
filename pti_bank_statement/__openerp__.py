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
    'name': 'Account Bank Statement',
    'category': 'account',
    'version': '1.0',
    'depends': ['account'],
    'author': 'Port Cities',
    'description': '''
    Account Bank Statement:\n
    This improve functionality bank statement by adding some control.\n
    - Add Validation on Starting Date and Ending Date\n
    - Add Validation on Start Balance and Ending Balance\n
    - Add Balance on each Bank Statement Line\n
    - Add Date Validation on Bank Statement Line\n
    - Add Internal Transfer Wizard\n
    ''',
    'data': [
        'security/bank_statement_security.xml',
        'views/account_bank_view.xml',
        'views/account_journal_view.xml',
        'views/res_config_view.xml',
        'wizard/account_payment_wizard_view.xml',
        'data/bank_statement_data.xml',
    ],
    'installable': True,
    'active': False,
    'auto_install': False
}

