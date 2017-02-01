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
    'name': 'PTI: Customer Order',
    'version': '1.0',
    'author': 'Port Cities',
    'description': """
v1.0
----
Modul Customer Order\n
- add returned products\n
- replace discount to discount_m2m\n
- change calculation based discount
- change calculation based return product
v.1.1
Free Product
    1. add free product use wizard
    2. price free product include tax
    3. subtotal for product will negative
@bima

    """,
    'website': 'http://portcitiesindonesia.com',
    'depends': ["pti_additional_models", ],
    'category': 'Sale Management',
    'data': [
        'wizard/list_free_product.xml',
        'data/temporary_customer.xml',
        'data/decimal_precision.xml',
        'security/ir.model.access.csv',
        'security/ir.rule.xml',
        'view/customer_order_view.xml',
        'view/sale_input_mode.xml',
        'security/menu_groups.xml',
             ],

    'installable': True,
    'application': True,
    'auto_install': False
}

