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

from openerp import models, fields, api, _
from openerp.exceptions import UserError

class product_brand(models.Model):
    _name = "product.brand"
    
    name = fields.Char('Name')
    status = fields.Boolean('Active')

    @api.model
    def create(self, values):
        res = self.search([('name', '=', values['name'])])
        # to avoid duplicate name
        if res.id:
            raise UserError(_(res.name+" already exist."))
        return super(product_brand, self).create(values)

class product_tags(models.Model):
    _name = "product.tags"
    
    name = fields.Char('Name')
    status = fields.Boolean('Active')

    @api.model
    def create(self, values):
        res = self.search([('name', '=', values['name'])])
        # to avoid duplicate name
        if res.id:
            raise UserError(_(res.name+" already exist."))
        return super(product_tags, self).create(values)
    
class outlet(models.Model):
    _name = "outlet.outlet"
    
    name_detail = fields.Char('Detail Name')
    name = fields.Char('Code')

class outlet_category(models.Model):
    _name = "outlet.category"
    
    name_detail = fields.Char('Detail Name')
    name = fields.Char('Code')
    

class distribution_channel(models.Model):
    _name = "distribution.channel"
    
    name_detail = fields.Char('Detail Name')
    name = fields.Char('Code')

class retur_reason(models.Model):
    _name="retur.reason"
    
    name_detail = fields.Char('Detail Reason')
    name = fields.Char('Reason')
    account_id = fields.Many2one("account.account","Account")  
    
class sub_distribution_channel(models.Model): 
    _name = "sub.distribution.channel"
    
    name_detail = fields.Char('Detail Name')
    name = fields.Char('Code')

class discount(models.Model):
    _name = "discount.discount"
    
    name = fields.Char('Name', required=True)
    percentage = fields.Float('Percentage')
    expired_date = fields.Date(string='Expired Date')
    status = fields.Boolean('Status')
    type = fields.Selection([('volume', 'volume'), ('additional', 'additional'),('sale_order', 'sale_order'), ('extra', 'extra')], 'Type')
    brand = fields.Many2one('product.brand', 'Brand')
    account_id = fields.Many2one("account.account","Account")
    sequence_discount = fields.Selection([('1', '1'), ('2', '2'),('3', '3'), ('4', '4'),('5', '5'), ('6', '6')], 'Sequence calculate discount')

class ptiPayment(models.Model):
    _name = "payment.category"
    
    name_detail = fields.Char('Detail Name')
    name = fields.Char('Code')

class area(models.Model):
    _name = "area.area"
     
    lead_time = fields.Integer('Lead Time')
    name_detail = fields.Char('Detail Name')
    name = fields.Char('Code')

class order_method(models.Model):
    _name = "order.method"
    
    name = fields.Char('Code')
    detail_name = fields.Char('Detail name')
