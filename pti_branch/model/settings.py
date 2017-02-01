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

from openerp.osv import fields, osv

class setting_sales(osv.TransientModel):
    _inherit = 'sale.config.settings'

    def update_setting(self, cr, uid, **args):
        ids = self.search(cr, uid, [])
        cfg = {
            'group_uom': 1, 
            'default_invoice_policy': 'delivery',
            'group_sale_delivery_address': 1,
            'group_discount_per_so_line': 1,
            'sale_pricelist_setting': 'percentage'
        }
        if ids:
            o = self.browse(cr, uid, ids[-1])
            o.write(cfg)
            o.execute()
        else:
            id2 = self.create(cr, uid, cfg)
            self.browse(cr, uid, id2).execute()
        return True


class setting_inventory(osv.TransientModel):
    _inherit = 'stock.config.settings'

    def update_setting(self, cr, uid, **args):
        ids = self.search(cr, uid, [])
        cfg = {
            'group_stock_multiple_locations': 1,
            'group_stock_adv_location': 1,
            'group_uom': 1
        }
        if ids:
            o = self.browse(cr, uid, ids[-1])
            o.write(cfg)
            o.execute()
        else:
            id2 = self.create(cr, uid, cfg)
            self.browse(cr, uid, id2).execute()
        return True


class setting_account(osv.TransientModel):
    _inherit = 'account.config.settings'

    def update_setting(self, cr, uid, **args):
        ids = self.search(cr, uid, [])
        cfg = {
            'group_proforma_invoices': True,
            'group_multi_currency': True
        }
        if ids:
            o = self.browse(cr, uid, ids[-1])
            o.write(cfg)
            o.execute()
        else:
            id2 = self.create(cr, uid, cfg)
            self.browse(cr, uid, id2).execute()
        return True

