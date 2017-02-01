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

from openerp.osv import osv,fields
import openerp.addons.decimal_precision as dp
from openerp import models,api,fields,_
from openerp.exceptions import UserError
#!/usr/bin/env python
# -*- coding: utf-8 -*-

class stock_picking_type(models.Model):
    _inherit='stock.picking.type'
    
    apply_mto=fields.Boolean('Apply Procurement Rules')
    
class stock_move(models.Model):
    _inherit='stock.move'
    
    def create(self, cr, uid, vals, context=None):
        picking=self.pool.get('stock.picking')
        if 'picking_id' in vals:
            picking_src=picking.browse(cr,uid,vals['picking_id'],context=context)
            if picking_src.picking_type_id.apply_mto==True:
                vals['procure_method']='make_to_order'
        return super(stock_move,self).create(cr,uid,vals,context=context)

class procurement_order(models.Model):
    _inherit = 'procurement.order'
    
    @api.model
    def create(self, values):
        # i don't know how to set automatically with settings in odoo 9
        # Set rule_id WH/Stock to WH/Staging pull rule if location procurement is Staging location to avoid exception
        if 'location_id' in values:
            ir_model_obj = self.env['ir.model.data']
            loc_stag_id = ir_model_obj.get_object('pti_stock_default_mto', 'ndc_staging')
            if loc_stag_id.id == values['location_id']:
                proc_rule = ir_model_obj.get_object('pti_stock_default_mto','stock_2_staging')
                values['rule_id'] = proc_rule.id
        return super(procurement_order,self).create(values)

