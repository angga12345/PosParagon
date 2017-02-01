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
    'name': 'Report Consumer Promo MDS',
    'category': 'account',
    'version': '1.0',
    'depends': ['base', 'point_of_sale'],
    'author': 'Port Cities',
    'description': '''
    v.1.0 \n
    
   Add new MDS Nasional and MDS Per Store Report\n
   author: Fachrian Luthfi R \n
    ''',
    'data': [
        'wizards/consumer_promo_nasional.xml',
        'wizards/consumer_promo_per_store.xml',
        'views/consumer_nasional_action.xml',
        'views/consumer_per_store_action.xml',
    ],
    'installable': True,
    'active': False,
    'auto_install': False
}
