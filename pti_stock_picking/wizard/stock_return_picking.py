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
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.osv import osv, fields
from openerp import api
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError
import logging
_log = logging.getLogger(__name__)

class stock_return_picking(osv.osv_memory):
    _inherit = 'stock.return.picking'

    _columns = {
        'picking_id': fields.many2one('stock.picking', 'Picking Number'),
        'all_product': fields.boolean('Reverse All Products'),
        'move_ids': fields.many2many('stock.move', 'stock_return_move', 'return_id', 'move_id', 'Moves',
            domain="[('picking_id', '=', picking_id)]"),
        'product_ids': fields.many2many('product.product', 'stock_return_product', 'return_id', 'product_id', 'Select Product'),
        'retur_reason':fields.many2one('retur.reason','Retur Reason'),
        'is_loc_name':fields.boolean('is stock')
    }
    
    @api.multi
    def create_returns(self):
        res= super(stock_return_picking, self).create_returns()
        pick_obj = self.env['stock.picking']
        context=self._context
        record_id = context.get('active_id', False) or False
        pick = pick_obj.browse(record_id)
        pick2_id=pick_obj.search([('origin','=',pick.name)], limit=1)
        pick2=pick_obj.browse(pick2_id.id)
        pick2.write({'retur_reason':self.retur_reason.id})
        return res

    def default_get(self, cr, uid, fields, context=None):
        """
         To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary with default values for all field in ``fields``
        """
        result1 = []
        if context is None:
            context = {}
        if context and context.get('active_ids', False):
            if len(context.get('active_ids')) > 1:
                raise osv.except_osv(_('Warning!'), _("You may only return one picking at a time!"))
        res = super(stock_return_picking, self).default_get(cr, uid, fields, context=context)
        record_id = context and context.get('active_id', False) or False
        uom_obj = self.pool.get('product.uom')
        pick_obj = self.pool.get('stock.picking')
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        quant_obj = self.pool.get("stock.quant")
        chained_move_exist = False
        product_ids = []
        if pick:
            #get is_loc_name value from is_retur stock_picking_type
            is_loc=False
            cr.execute('select t.return_picking_type_id from  stock_picking s, stock_picking_type t '\
                                'where s.picking_type_id=t.id and s.id=%s',[pick.id])
            result = cr.dictfetchall()
            if result[0].get('return_picking_type_id'):
                cr.execute('select is_retur from stock_picking_type '\
                                    'where  id=%s', [(result[0].get('return_picking_type_id'))])
                result2 = cr.dictfetchall()
                is_loc=result2[0].get('is_retur')
            else:
                raise UserError(_("Your picking is do not have picking retur!"))
            
            if pick.state != 'done':
                raise UserError(_("You may only return pickings that are Done!"))

            for move in pick.move_lines:
                product_ids.append(move.product_id.id)
                if move.move_dest_id:
                    chained_move_exist = True
            if 'is_loc_name' in fields:
                res.update({'is_loc_name':is_loc})
            if 'product_return_moves' in fields:
                res.update({'product_return_moves': []})
            if 'picking_id' in fields:
                res.update({'picking_id': pick.id})
            if 'move_dest_exists' in fields:
                res.update({'move_dest_exists': chained_move_exist})
            if 'parent_location_id' in fields and pick.location_id.usage == 'internal':
                res.update({'parent_location_id':pick.picking_type_id.warehouse_id and pick.picking_type_id.warehouse_id.view_location_id.id or pick.location_id.location_id.id})
            if 'original_location_id' in fields:
                res.update({'original_location_id': pick.location_id.id})
            if 'location_id' in fields:
                res.update({'location_id': pick.location_id.id})
            if 'retur_reason' in fields:
                res.update({'retur_reason': pick.retur_reason.id})
        return res


    def onchange_picking_id(self, cr, uid, ids, picking_id, context=None):
        pick_obj = self.pool.get('stock.picking')
        product_ids = []
        if picking_id:
            pick = pick_obj.browse(cr, uid, picking_id)
            for move in pick.move_lines:
                product_ids.append(move.product_id.id)
        domain = [('id','in',tuple(product_ids))]
        return {'domain': {'product_ids': domain}}
        
        
    def onchange_all_product(self, cr, uid, ids, all_product, picking_id, context=None):
        """ If all_product = True it will return all related stock move
        @param all_product: Reverse All Product
        @param picking_id: Picking
        @param move_ids: Current Selected Moves
        @return: Product Return Moves
        """
        return_moves = []
        pick_obj = self.pool.get('stock.picking')
        uom_obj = self.pool.get('product.uom')
        quant_obj = self.pool.get("stock.quant")
        if all_product:
            pick = pick_obj.browse(cr, uid, picking_id)
            for move in pick.move_lines:
                if move.move_dest_id:
                    chained_move_exist = True
                #Sum the quants in that location that can be returned (they should have been moved by the moves that were included in the returned picking)
                qty = 0
                quant_search = quant_obj.search(cr, uid, [('history_ids', 'in', move.id), ('qty', '>', 0.0), ('location_id', 'child_of', move.location_dest_id.id)], context=context)
                for quant in quant_obj.browse(cr, uid, quant_search, context=context):
                    if not quant.reservation_id or quant.reservation_id.origin_returned_move_id.id != move.id:
                        qty += quant.qty
                qty = uom_obj._compute_qty(cr, uid, move.product_id.uom_id.id, qty, move.product_uom.id)
                return_moves.append((0, 0, {'product_id': move.product_id.id, 'quantity': qty, 'move_id': move.id}))

        return {'value': {'product_return_moves': return_moves}}
        
    def onchange_product_ids(self, cr, uid, ids, product_ids, picking_id, context=None):
        """ If all_product = True it will return all related stock move
        @param all_product: Reverse All Product
        @param picking_id: Picking
        @param move_ids: Current Selected Moves
        @return: Product Return Moves
        """
        return_moves = []
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        uom_obj = self.pool.get('product.uom')
        quant_obj = self.pool.get("stock.quant")
        if product_ids:
            for x in product_ids:
                product_id = len(x)>1 and x[1] or False
                if product_id:
                    move_ids = move_obj.search(cr, uid, [('picking_id','=',picking_id),('product_id','=',product_id)])
                    if move_ids:
                        for move in move_obj.browse(cr, uid, move_ids):
                            qty = 0
                            quant_search = quant_obj.search(cr, uid, [('history_ids', 'in', move.id), ('qty', '>', 0.0), ('location_id', 'child_of', move.location_dest_id.id)], context=context)
                            for quant in quant_obj.browse(cr, uid, quant_search, context=context):
                                if not quant.reservation_id or quant.reservation_id.origin_returned_move_id.id != move.id:
                                    qty += quant.qty
                            qty = uom_obj._compute_qty(cr, uid, move.product_id.uom_id.id, qty, move.product_uom.id)
                            return_moves.append((0, 0, {'product_id': move.product_id.id, 'quantity': qty, 'move_id': move.id}))

        return {'value': {'product_return_moves': return_moves}}

