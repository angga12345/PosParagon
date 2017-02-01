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

# -*- encoding: utf-8 -*-
{
    'name': 'Indonesian - Accounting',
    'version': '1.0',
    'author': 'PortCities',
    'website': 'http://www.PortCitiesIndonesia.com',
    'category': 'Localization/Account Charts',
    'description': """
Indonesia accounting chart and localization.
=======================================================
Also:\n
    - create Chart of Accounts
    - activates IDR currency.
    - sets up Indonesian taxes.
        -> Sale 10% exclude price (VAT Out Account)\n
        -> Sale 10% include price (VAT Out Account)\n
        -> Purchase 10% include price (VAT In Account)\n
        -> Purchase 10% exclude price (VAT In Account)\n
    - set up account bank
        > bank mandiri
        > bank bca
        > bank bni
        > bank cimb
        > bank muamalat
        > bank mega
        > bank panin
    - set up account journal
    """,
    'depends': ['account_accountant','pti_branch'],
    'demo': [ ],
    'data': [
        'data/account_chart_template.xml',
        'data/account.account.template.csv',
        'data/account_chart_template_refs.xml',
        #'data/account.chart.template.csv',
        'data/account_tax_template.xml',
        'data/account_tax.xml',
        'data/localization.xml',
        'data/account_chart_template.yml',
        'data/res.lang.csv',
        'data/res.bank.csv',
        'data/res.partner.bank.csv',
        'data/account.journal.xml'
    ],
    'installable': True,
}

