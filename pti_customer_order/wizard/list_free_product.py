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

# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.odoo.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.osv import osv
import openerp.addons.decimal_precision as dp
from datetime import datetime
from openerp.exceptions import UserError, ValidationError

class listFreeProduct(models.TransientModel):
    _name = 'sale.free.product'
    _description = 'Free Product'

    sale_id = fields.Many2one('sale.order', 'Reference')
    item_ids = fields.One2many('sale.free.product.list', 'free_product_line', 'Items')
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(listFreeProduct, self).default_get(cr, uid, fields, context=context)
        res.update({'sale_id' : context.get('active_id') or False})
        return res
    @api.one
    def add_products(self):
        # Create new and update existing pack operations
        active_id = self.env.context.get('active_id') or False
        sol = self.env['sale.order.line']
        for list in self.item_ids:
            product_template = list.product_id.product_tmpl_id.id
            product_template = self.env['product.template'].search([('id','=',product_template)])
            brand = 0
            for tag_m2m in product_template.tags:
                if 'brand:' in tag_m2m.name:
                    brand = tag_m2m.id
                    break
            acc_tax = self.env['account.tax']
            tax_id = acc_tax.search([('name','=','PPN'),('type_tax_use','=','sale')],limit=1)
            temp = {
                'order_id': active_id,
                'product_id': list.product_id.id,
                'product_uom_qty': list.product_uom_qty,
                'product_uom' : list.product_uom.id,
                'price_unit' : list.price_unit,
                'customer_lead' : list.customer_lead,
                'name' : list.name,
                'tax_id' : [(6, 0, [tax_id.id])],
                'product_brand' : brand,
                'qty_to_invoice' : list.product_uom_qty,
                'qty_delivered' : list.product_uom_qty,
                'is_free' : True,
                'price_unit_hidden' : list.price_unit,
            }
            
            res = sol.search([('order_id','=', active_id),('product_id','=',list.product_id.id)])
            qty = 0.0
            flag = True
            for sol_detail in res:
                if flag:
                    temp['discount_m2m'] = [(6, 0, [d.id for d in sol_detail.discount_m2m])]
                    flag = False
                qty += sol_detail.product_uom_qty
            if not res:
                raise UserError(_("Sory There is no Free Product match with sale order line!, please check before continue...."))
            
            if list.product_uom_qty > qty:
                raise UserError(_("Quantity of free product can't greater than order product."))

            sol.with_context(tz={}).create(temp)
        return True


class stock_transfer_details_items(models.TransientModel):
    _name = 'sale.free.product.list'
    _description = 'List free product'

    free_product_line =  fields.Many2one('sale.free.product','Sale Reference')
    name = fields.Char('Description')
    product_id = fields.Many2one('product.product','Product', required=True)
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    product_uom = fields.Many2one('product.uom', string='Unit of Measure', required=True)
    price_unit = fields.Float('Unit Price')
    customer_lead = fields.Float('Delivery Lead Time', required=True, default=0.0)
    sale_id = fields.Many2one('sale.order.input', 'SO reference')
    
    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not (self.product_uom and (self.product_id.uom_id.category_id.id == self.product_uom.category_id.id)):
            vals['product_uom'] = self.product_id.uom_id

        product = self.product_id.with_context(
            lang=self.free_product_line.sale_id.partner_id.lang,
            partner=self.free_product_line.sale_id.partner_id.id,
            quantity=self.product_uom_qty,
            date=self.free_product_line.sale_id.date_order,
            pricelist=self.free_product_line.sale_id.pricelist_id.id,
            uom=self.product_uom.id
        )
        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = 'Discount Extra Promo'
        acc_tax = self.env['account.tax']
        tax_id = acc_tax.search([('name','=','PPN'),('type_tax_use','=','sale')])
        if self.free_product_line.sale_id.pricelist_id and self.free_product_line.sale_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(product.price, product.taxes_id, tax_id)
            
        self.update(vals)
        return {'domain': domain}

