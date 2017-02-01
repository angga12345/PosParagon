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

import datetime
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError, ValidationError
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import SUPERUSER_ID

class SaleOrderInputMode(models.Model):
    _name = "sale.order.input"
    
    @api.model
    def _get_defaultDC(self):
        return self.env.user.partner_id.dc_id

    dc_id = fields.Many2one('res.partner','Distribution Center',default=_get_defaultDC)
    sales_id = fields.Many2one('res.partner', string='Salesperson')
    order_method = fields.Many2one('order.method','Order Method')
    partner_id = fields.Many2one('res.partner','Customer')
    name = fields.Char('Reference')
    order_line = fields.One2many('sale.order.line.input', 'order_id')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    so_id = fields.Many2one('sale.order', string='Sale Order')
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', help="Pricelist for current sales order.")
    
    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            return
        else:
            default = self.env['stock.warehouse'].search([('dc_id', '=', self.env.user.partner_id.dc_id.id)], limit=1)
            values = {'warehouse_id' : False}
            dc_id = False
            if self.dc_id:
                dc_id = self.dc_id.id
            else:
                dc_id = self.partner_id.dc_id.id
                
            ir_model_data = self.env['ir.model.data']
            order_method_id = ir_model_data.get_object_reference('__export__', 'pti_order_method_s')[1]
            
            if self.partner_id.is_consignment:
                warehouse_ids = self.env['stock.warehouse'].search([('dc_id', '=', dc_id),
                                                                    ('name', '=', self.partner_id.name)], limit=1)
                order_method_id = ir_model_data.get_object_reference('__export__', 'pti_order_method_c')[1]
                values = {'warehouse_id' : warehouse_ids.id, 'order_method' : order_method_id}
            elif self.partner_id.ref == 'tmp.customer':
                warehouse_ids = self.env['stock.warehouse'].search([('dc_id', '=', dc_id),
                                                                    ('code', 'ilike', 'MW')], limit=1)
                order_method_id = ir_model_data.get_object_reference('__export__', 'pti_order_method_c')[1]
                values = {'warehouse_id' : warehouse_ids.id, 'order_method' : order_method_id}
            elif dc_id:
                warehouse_ids = self.env['stock.warehouse'].search([('dc_id', '=', dc_id),
                                                                    ('name', '=', self.dc_id.name)], limit=1)
                values = {'warehouse_id' : warehouse_ids.id, 'order_method' : order_method_id}
            else:
                values = {'warehouse_id' : default.id, 'order_method' : order_method_id}
            self.update(values)
            
    @api.multi
    def create_so(self):
        self.ensure_one()
        sale = self.env['sale.order']
        model, uom_id = self.pool.get('ir.model.data').get_object_reference(self._cr, self._uid, 'pti_additional_models', 'product_uom_pcs')
        sale_order_line = self.env['sale.order.line']
        for so in self:
            sale_order = sale.create({'dc_id' : so.dc_id.id,
                         'sales_id' : so.sales_id.id,
                         'order_method' : so.order_method.id,
                         'partner_id' : so.partner_id.id,
                         'warehouse_id' : so.warehouse_id.id,
                         'pricelist_id' : so.pricelist_id.id
                         })
            for line in so.order_line:
                price_unit = 0
                if sale_order.partner_id:
                    product = line.product_id.with_context(
                        lang=sale_order.partner_id.lang,
                        partner=sale_order.partner_id.id,
                        quantity=line.product_uom_qty,
                        date=sale_order.date_order,
                        pricelist=sale_order.pricelist_id.id,
                        uom=uom_id
                    )
                    tax_id = line.product_id.taxes_id if line.product_id.taxes_id else False
                    price_unit_hidden = price_unit = self.env['account.tax']._fix_tax_included_price(product.price, product.taxes_id, tax_id)
                sql = " select discount_id as d,brand as b from  "\
                         " (select * from "\
                         "   (select discount_id from customer_discount where partner_id = "+ str(so.partner_id.id) +") as disc_cust  "\
                         "   join discount_discount dd on dd.id = disc_cust.discount_id and dd.status = True) as brand_cust "\
                         "   join (select id from (select product_brand_id from product_brand_product_template_rel where product_template_id="+ str(line.product_id.product_tmpl_id.id) +") as data "\
                         "   join product_brand pb on pb.id = data.product_brand_id and pb.name ilike 'brand:%') as fixed_brand  "\
                         "   on fixed_brand.id=brand_cust.brand; "
                self.env.cr.execute(sql)
                res = self.env.cr.dictfetchall()
                discount_m2m = []
                product_brand = False
                if res:
                    discount_m2m = [d['d'] for d in res]
                    product_brand = res[0]['b']
                tax_id = self.env['account.tax'].search([('type_tax_use','=','sale')], limit=1)
                new_line = sale_order_line.create({'product_id' : line.product_id.id,
                                        'product_uom_qty' : line.product_uom_qty,
                                        'order_id' : sale_order.id,
                                        'name' : line.product_id.name,
                                        'customer_lead' : 1,
                                        'product_uom' : uom_id,
                                        'price_unit' : price_unit,
                                        'price_unit_hidden' : price_unit_hidden,
                                        'discount_m2m' : [(6, 0, discount_m2m)],
                                        'product_brand' : product_brand,
                                        'tax_id' : [(6, 0, [tax_id.id])]})
                new_line.update_amount()
        self.name = sale_order.name
        self.so_id = sale_order.id
        return {
            'name': 'Quotation',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'sale.order',
            'res_id': sale_order.id, 
            'domain': [('id','=',sale_order.id)],
            'type': 'ir.actions.act_window',
        }


class SaleOrderLineInputMode(models.Model):
    _name = "sale.order.line.input"
    
    name = fields.Char('Describtion')
    order_id = fields.Many2one('sale.order.input', string='Order Reference', required=True, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict', required=True)
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)

