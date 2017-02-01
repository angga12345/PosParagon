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
from openerp.exceptions import UserError, ValidationError, Warning
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import logging
import string

_logger = logging.getLogger(__name__)

class discountsSO(models.Model):
    _name = "sale.order.discounts"
    
    discount_id = fields.Many2one('discount.discount', 'Discount SO')
    order_id = fields.Many2one('sale.order', string='Order reference', required=True, ondelete='cascade', index=True, copy=False)

    @api.multi
    def unlink(self):
        for disc in self:
            order_id = disc.order_id.id
            discount_id = disc.discount_id.id
            self._cr.execute("select id from sale_order_line where order_id=%s" % order_id)
            line_ids = [x[0] for x in self._cr.fetchall()]
            query = "DELETE FROM discount_discount_sale_order_line_rel "\
                "where discount_discount_id=%s "\
                "and sale_order_line_id in %s"
            self._cr.execute(query, (discount_id,tuple(line_ids)))
            self.env['sale.order.line'].search([('id','in',line_ids)]).write({'date_change_disc': fields.datetime.now()})
            self.invalidate_cache()
            
        return super(discountsSO, self).unlink()
    
 
class customer_order(models.Model):
    _inherit = "sale.order"
    
    discount_cust_order = fields.One2many('sale.order.discounts', 'order_id', copy=True, string='Discount Sale Order')
    order_method = fields.Many2one('order.method','Order Method', required=True)
    allow_finance = fields.Boolean('Can edit unit price', default=False)
    allow_sales = fields.Boolean('Can edit discount', default=True)

    @api.model
    def create(self, vals):
        if vals.get('client_order_ref'):
            temp_client_order_ref = vals['client_order_ref']
            vals['client_order_ref'] = temp_client_order_ref.upper()
        result = super(customer_order, self).create(vals)
        return result

    @api.multi
    def write(self, vals):
        if vals.get('client_order_ref'):
            temp_client_order_ref = vals['client_order_ref']
            vals['client_order_ref'] = temp_client_order_ref.upper()
        res = super(customer_order, self).write(vals)
        return res

    @api.multi
    def button_dummy(self):
        super(customer_order, self).button_dummy()
        disc_cus = []
        dco_ids = []
        multibrand_discounts = [] # 3 TYPE DISCOUNT (sale_order,volume,additional) with brand
        disc_brand = []
        global_discounts = []
        disc_brand_prods = []
        ''' GET ALL DISCOUNT GLOBAL (DISCOUNT TYPE : sale_order) '''
        for dco in self.discount_cust_order:
            dco_ids.append(dco.discount_id.id)
            multibrand_discounts.append(dco.discount_id.id)
            if dco.discount_id.brand.id:
                disc_brand.append(dco.discount_id.brand.id)
            else:
                global_discounts.append(dco.discount_id.id)
        ''' GET ALL DISCOUNT CUSTOMER (DISCOUNT TYPE : volume and additional) '''
        disc_customers = self.env['customer.discount'].search([('partner_id','=',self.partner_id.id)])
        for disc in disc_customers :
            disc_cus.append(disc.discount_id.id)
            multibrand_discounts.append(disc.discount_id.id)
            disc_brand.append(disc.discount_id.brand.id)

        querygetprod = ""
        if len(disc_brand)==0:
            querygetprod = "select product_template_id from product_brand_product_template_rel "
        elif len(disc_brand)==1:
            querygetprod = "select product_template_id from product_brand_product_template_rel "\
                           "where product_brand_id = %s" % disc_brand[0]
        else:
            querygetprod = "select product_template_id from product_brand_product_template_rel "\
                           "where product_brand_id in %s" % str(tuple(disc_brand))

        if querygetprod!= "":
            self._cr.execute(querygetprod)
            prods = self._cr.fetchall()
            for prod in prods :
                disc_brand_prods.append(prod[0])

        for sol in self.order_line :
            querygetbrand = "select product_brand_id from product_brand_product_template_rel "\
                           "where product_template_id=%s limit 1" % sol.product_id.product_tmpl_id.id
            self._cr.execute(querygetbrand)
            sol_prod_brands = self._cr.fetchall()
            found_brand = False
            extra_disc_ids = []
            # keep extra discount
            for extra in sol.discount_m2m:
                if extra.type == 'extra':
                    extra_disc_ids.append(extra.id)

            if sol.product_id.product_tmpl_id.id in disc_brand_prods:
                found_brand = True
            if found_brand:
                disc_ids_temp = []
                # improve this get object in outside loop insert into array then loop manual without search again
                prod_brand_disc = self.env['discount.discount'].search([('brand','=',sol_prod_brands[0][0]), 
                                                                        ('id','in',multibrand_discounts)])
                for pbd in prod_brand_disc:
                    disc_ids_temp.append(pbd.id)
                # discount global apply to all product
                for _global in global_discounts:
                    disc_ids_temp.append(_global)
                sol.update({"discount_m2m" : [(6, 0, disc_ids_temp + extra_disc_ids)] })
            else:
                disc_ids_temp = []
                for _global in global_discounts:
                    disc_ids_temp.append(_global)
                sol.update({"discount_m2m" : [(6, 0, disc_ids_temp + extra_disc_ids)] })
        return True

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(customer_order, self).onchange_partner_id()
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
    def action_invoice_create(self, grouped=False, final=False):
        super(customer_order, self).action_invoice_create(grouped, final)
        for sale in self:
            for line in sale.picking_ids:
                if line.backorder_id.id == False and line.is_retur == False:
                    if line.state_shipment == 'done':
                        if self._context.get('open_gan', True):
                            return self.action_view_invoice()
                    else:
                        raise Warning(_('you should create picking shipment first and picking shipment should done'))


class customer_sale_order_line(models.Model):
    _inherit = "sale.order.line"

    editable_discount = fields.Boolean(compute='_change_view_sales', string='Can Edit Discount', default=False)
    editable_price = fields.Boolean(compute='_change_view_finance', string='Can Edit Unit Price', default=False)
    price_unit_hidden = fields.Float('Unit Price Hidden', digits=dp.get_precision('Product Price'), default=0.0)
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Finish Goods'), required=True, default=1)
    qty_delivered = fields.Float(string='Delivered', copy=False, digits=dp.get_precision('Finish Goods'), default=0)
    qty_to_invoice = fields.Float(
        compute='_get_to_invoice_qty', string='To Invoice', store=True, readonly=True,
        digits=dp.get_precision('Finish Goods'), default=0)
    qty_invoiced = fields.Float(
        compute='_get_invoice_qty', string='Invoiced', store=True, readonly=True,
        digits=dp.get_precision('Finish Goods'), default=0)
    

    @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'order_id.state')
    def _get_to_invoice_qty(self):
        super(customer_sale_order_line, self)._get_invoice_qty()

    @api.depends('order_id.allow_sales')
    def _change_view_sales(self):
        for line in self:
            line.update({
                         'editable_discount' : line.order_id.allow_sales,
                         'price_unit' : line.price_unit_hidden if line.price_unit <= 0 else line.price_unit 
                         })
            
    @api.depends('order_id.allow_finance')
    def _change_view_finance(self):
        for line in self:
            line.update({
                         'editable_price' : line.order_id.allow_finance,
                         'price_unit' : line.price_unit_hidden if line.price_unit <= 0 else line.price_unit 
                         })

    @api.onchange('product_uom_qty')
    def _onchange_product_id_check_availability(self):
        return
    
    @api.multi
    def invoice_line_create(self, invoice_id, qty):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if not float_is_zero(qty, precision_digits=precision):
                if line.qty_delivered - line.qty_returned > 0:
                    vals = line._prepare_invoice_line(qty=qty)
                    vals.update({'invoice_id': invoice_id, 'sale_line_ids': [(6, 0, [line.id])]})
                    self.env['account.invoice.line'].create(vals)

    @api.depends('state', 'product_uom_qty', 'qty_delivered', 'qty_to_invoice', 'qty_invoiced', 'qty_returned')
    def _compute_invoice_status(self):
        """
        Compute the invoice status of a SO line. Possible statuses:
        - no: if the SO is not in status 'sale' or 'done', we consider that there is nothing to
          invoice. This is also hte default value if the conditions of no other status is met.
        - to invoice: we refer to the quantity to invoice of the line. Refer to method
          `_get_to_invoice_qty()` for more information on how this quantity is calculated.
        - upselling: this is possible only for a product invoiced on ordered quantities for which
          we delivered more than expected. The could arise if, for example, a project took more
          time than expected but we decided not to invoice the extra cost to the client. This
          occurs onyl in state 'sale', so that when a SO is set to done, the upselling opportunity
          is removed from the list.
        - invoiced: the quantity invoiced is larger or equal to the quantity ordered.
        - returned: the quantity returned by customer
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if line.state not in ('sale', 'done'):
                line.invoice_status = 'no'
            elif line.qty_invoiced>0 and line.qty_invoiced==(line.qty_delivered-line.qty_returned):
                line.invoice_status = 'invoiced'
            elif not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                line.invoice_status = 'to invoice'
            elif line.state == 'sale' and line.product_id.invoice_policy == 'order' and\
                    float_compare(line.qty_delivered, line.product_uom_qty, precision_digits=precision) == 1:
                line.invoice_status = 'upselling'
            elif float_compare(line.qty_invoiced, line.product_uom_qty, precision_digits=precision) >= 0:
                line.invoice_status = 'invoiced'
            else:
                line.invoice_status = 'no'
                
    @api.depends('product_uom_qty', 'discount_m2m', 'price_unit', 'tax_id','date_change_disc', 'qty_delivered', 'qty_returned')
    def _compute_amount(self):
        for line in self:
            price = line.price_unit
            for discount_product in line.discount_m2m:
                if discount_product.id:
                    price = price * (1 - (discount_product.percentage or 0.0) / 100.0)

            delivered = line.product_uom_qty
            if line.qty_delivered > 0 and line.qty_delivered <= line.product_uom_qty:
                delivered = line.qty_delivered
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, 
                                                delivered,
                                                product=line.product_id, partner=line.order_id.partner_id)
            if line.is_free:
                line.update({
                    'price_tax': (taxes['total_included'] - taxes['total_excluded']) * -1,
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'] * -1.0,
                    'price_after_discounts' : price,
                })
            else:
                line.update({
                    'price_tax': taxes['total_included'] - taxes['total_excluded'],
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                    'price_after_discounts': price,
                })
    @api.one
    def update_amount(self):
        price = self.price_unit
        for discount_product in self.discount_m2m:
            if discount_product.id:
                price = price * (1 - (discount_product.percentage or 0.0) / 100.0)
        taxes = self.tax_id.compute_all(price, self.order_id.currency_id,
                                        self.product_uom_qty,
                                        product=self.product_id, partner=self.order_id.partner_id)
        self.update({
            'price_tax': taxes['total_included'] - taxes['total_excluded'],
            'price_total': taxes['total_included'],
            'price_subtotal': taxes['total_excluded'],
            'price_after_discounts' : price,
        })
    
    @api.depends('product_id.invoice_policy', 'order_id.state')
    def _compute_qty_delivered_updateable(self):
        for line in self:
            line.qty_delivered_updateable = line.product_id.invoice_policy in ('order', 'delivery') and line.order_id.state == 'sale' and line.product_id.track_service == 'manual'

    @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'order_id.state')
    def _get_to_invoice_qty(self):
        """
        Compute the quantity to invoice. If the invoice policy is order, the quantity to invoice is
        calculated from the ordered quantity. Otherwise, the quantity delivered is used.
        """
        for line in self:
            if line.order_id.state in ['sale', 'done']:
                if line.product_id.invoice_policy == 'order':
                    line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
                else:
                    line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    @api.depends('invoice_lines.invoice_id.state', 'invoice_lines.quantity')
    def _get_invoice_qty(self):
        """
        Compute the quantity invoiced. If case of a refund, the quantity invoiced is decreased. Note
        that this is the case only if the refund is generated from the SO.
        """
        for line in self:
            qty_invoiced = 0.0
            for invoice_line in line.invoice_lines:
                if invoice_line.invoice_id.state != 'cancel':
                    if invoice_line.invoice_id.type == 'out_invoice':
                        qty_invoiced += invoice_line.quantity
                    elif invoice_line.invoice_id.type == 'out_refund':
                        qty_invoiced -= invoice_line.quantity
            line.qty_invoiced = qty_invoiced

    @api.depends('price_subtotal', 'product_uom_qty')
    def _get_price_reduce(self):
        for line in self:
            line.price_reduce = line.price_subtotal / line.product_uom_qty if line.product_uom_qty else 0.0
        
    @api.model
    def addTaxToUnitPrice(self):
        acc_tax = self.env['account.tax']
        tax_id = acc_tax.search([('type_tax_use','=','sale')], limit=1)
        self.price_unit = self.price_unit + (self.price_unit * ((tax_id.amount or 0.0)/ 100.0))

    @api.multi
    def checkDiscountExist(self, sol_id, disc_id): 
        if not disc_id:
            return False
        self.env.cr.execute('''SELECT COUNT(*) 
                        FROM discount_discount_sale_order_line_rel 
                            WHERE sale_order_line_id=%s and discount_discount_id=%s''' ,(sol_id,disc_id))  
        res = self.env.cr.fetchone()
        if len(res)==0:
            return False
        else:
            return res[0]==1
    
    
    @api.multi
    def _action_procurement_create(self):
        """
        Create procurements based on quantity ordered. If the quantity is increased, new
        procurements are created. If the quantity is decreased, no automated action is taken.
        
        replace the old function to avoid calculation for free product
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        new_procs = self.env['procurement.order'] #Empty recordset
        for line in self:
            if line.state != 'sale' or line.is_free:
                continue
            qty = 0.0
            for proc in line.procurement_ids:
                qty += proc.product_qty
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                return False
            if not line.order_id.procurement_group_id:
                vals = line.order_id._prepare_procurement_group()
                line.order_id.procurement_group_id = self.env["procurement.group"].create(vals)

            vals = line._prepare_order_line_procurement(group_id=line.order_id.procurement_group_id.id)
            vals['product_qty'] = line.product_uom_qty - qty
            new_proc = self.env["procurement.order"].create(vals)
            new_procs += new_proc
        new_procs.run()
        return new_procs
                
    @api.model
    def create(self, values):
        if values['product_uom_qty']<=0:
            # it mean can't create sale.order.line
            return self
        ir_model_data = self.env['ir.model.data']
        finance_id = ir_model_data.get_object_reference('pti_branch', 'group_pti_branch_finance_admin')[1]
        is_finance = False
        for group in self.env.user.groups_id:
            if group.id == finance_id:
                is_finance = True
                break
        if values.get('price_unit'):
            values['price_unit_hidden'] = values['price_unit']
        elif values.get('price_unit_hidden'):
            values['price_unit'] = values['price_unit_hidden']
        line = super(customer_sale_order_line, self).create(values)
        return line
    
    @api.multi
    def write(self, values):
        ir_model_data = self.env['ir.model.data']
        finance_id = ir_model_data.get_object_reference('pti_branch', 'group_pti_branch_finance_admin')[1]
        is_finance = False
        for group in self.env.user.groups_id:
            if group.id == finance_id:
                is_finance = True
                break

        if values.get('price_unit'):
            values['price_unit_hidden'] = values['price_unit']
        elif values.get('price_unit_hidden'):
            values['price_unit'] = values['price_unit_hidden']
        line = super(customer_sale_order_line, self).write(values)        
        return line

    @api.model
    def GetDiscountBrand(self, partner_id, line):
        '''
        maybe can removed this method :: try to set discount use onchange_prodoct_id
        RESULT DISCOUNT IDS FROM CUSTOMER WHICH MATCH WITH PRODUCT TAGS
        @PARAM : line => SALE ORDER LINE OBJECT
        @PARAM : partner_id => GET FROM SALE ORDER
        '''
        result = []
        list_disc = partner_id.discount_customer
        product_template = line.product_id.product_tmpl_id.id
        product_template = self.env['product.template'].search([('id','=',product_template)])
        product_tags = product_template.tags
        for disc_o2m in list_disc:
            for tag in product_tags:
                # CHECK TAG DISCOUNT
                if tag.id == disc_o2m.discount_id.brand.id and disc_o2m.discount_id.status == True:
                    result.append(disc_o2m.discount_id.id)
        return result
    
    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(customer_sale_order_line, self)._prepare_invoice_line(qty=qty)
        res.pop("discount",None)
        if self.is_free:
            res.update({"price_unit" : (res['price_unit'] * -1)})
        disc_ids = []
        for d in self.discount_m2m:
            disc_ids.append(d.id)
        res.update({"product_brand" : self.product_brand.id,"quantity" : self.qty_delivered - self.qty_returned,
                    "qty_returned" : self.qty_returned or 0.0, "discount_m2m" : [(6, 0, disc_ids)], 
                    "is_free" : self.is_free})
        return res
    
    @api.multi
    def _get_delivered_qty(self):
        self.ensure_one()
        return_qty = 0.0
        '''
        select sum(product_uom_qty),product_uom,location_id from stock_move where picking_id in (107044, 107043, 107042) and product_id = 3 group by location_id,product_uom;
        '''      
        for move in self.procurement_ids.mapped('move_ids').filtered(lambda r: r.state == 'done' and not r.scrapped):
            if move.location_dest_id.usage == "internal":
                return_qty += move.product_uom_qty
        self.qty_returned = return_qty
        return super(customer_sale_order_line, self)._get_delivered_qty()
    
    product_brand = fields.Many2one('product.brand', "Brand")
    date_change_disc = fields.Datetime(string='Registration Date', default=lambda self: fields.datetime.now())
    discount_m2m = fields.Many2many('discount.discount',string="Discounts")
    qty_returned = fields.Float(string='Returned', copy=False,
                                 digits=dp.get_precision('Finish Goods'), default=0)
    price_after_discounts = fields.Float(compute='_compute_amount', string='Unit Price After Discount', default=0.0, store=True)
    is_free = fields.Boolean('Free product', default=False)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Monetary(compute='_compute_amount', string='Taxes', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    
    @api.multi
    @api.onchange('product_id','is_free')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not (self.product_uom and (self.product_id.uom_id.category_id.id == self.product_uom.category_id.id)):
            vals['product_uom'] = self.product_id.uom_id
        partner_id =self.order_id.partner_id.id
        if not partner_id:
            raise UserError(_("Please, fill customer first."))
        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=partner_id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )
        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name
        
        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = vals['price_unit_hidden'] = self.env['account.tax']._fix_tax_included_price(product.price, product.taxes_id, self.tax_id)
        
        if not self.is_free:
            sql = " select discount_id as d,brand as b from  "\
                     " (select * from "\
                     "   (select discount_id from customer_discount where partner_id = "+ str(partner_id) +") as disc_cust  "\
                     "   join discount_discount dd on dd.id = disc_cust.discount_id and dd.status = True) as brand_cust "\
                     "   join (select id from (select product_brand_id from product_brand_product_template_rel where product_template_id="+ str(self.product_id.product_tmpl_id.id) +") as data "\
                     "   join product_brand pb on pb.id = data.product_brand_id and pb.name ilike 'brand:%') as fixed_brand  "\
                     "   on fixed_brand.id=brand_cust.brand; "
            self.env.cr.execute(sql)
            res = self.env.cr.dictfetchall()
            if res:
                vals['discount_m2m'] = [d['d'] for d in res]
                vals['product_brand'] = res[0]['b']
            else:
                self.env.cr.execute("select pb.id from (select product_brand_id from product_brand_product_template_rel where product_template_id="+ str(self.product_id.product_tmpl_id.id) +") as data join  product_brand pb on pb.id = data.product_brand_id and pb.name ilike 'brand:%';")
                res = self.env.cr.dictfetchall()
                if res:
                    vals['product_brand'] = res[0]['id']
        self.update(vals)
        return {'domain': domain}
        
class stock_picking(models.Model):
    _inherit = "stock.picking"
    
    def do_transfer(self, cr, uid, ids, context=None):
        ids = isinstance(ids, (int, long)) and [ids] or ids
        super(stock_picking, self).do_transfer(cr, uid, ids, context)
        stock_pick = self.browse(cr, uid, ids, context)
        sale_order = stock_pick.sale_id.id
        sm_obj = self.pool.get('stock.move')
        sm_ids = sm_obj.search(cr, uid, [('picking_id','=',ids[0])])
        sol_obj = self.pool.get('sale.order.line')
        for sm_dt in sm_obj.browse(cr, uid, sm_ids, context):
            sol_id = sol_obj.search(cr, uid, [('order_id','=',sale_order),('product_id','=',sm_dt.product_id.id)])
            sol_obj.browse(cr, uid, sol_id, context)._compute_amount()
        return True
    
class product_template(models.Model):
    _inherit = "product.template"
    
    old_koitem = fields.Char('Korporate Code')
    tags = fields.Many2many('product.brand',string="Brand")
    ext_tags = fields.Many2many('product.tags',string="Tags")
    sale_delay =  fields.Float('Customer Lead Time', help="The average delay in days between the confirmation of the customer order and the delivery of the finished products. It's the time you promise to your customers.", default=0)
    project_code = fields.Char('Project Code')
    
    def _get_default_uom(self, cr, uid, context=None):
        model, uom_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'pti_additional_models', 'product_uom_pcs')
        return uom_id or False

    _defaults = {
        'uom_id': _get_default_uom, 
    }

