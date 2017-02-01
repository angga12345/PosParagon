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
from openerp import models, fields, api, _
from openerp.exceptions import UserError

class procurement_order(models.Model):
    _inherit = 'procurement.order'
    
    first_origin = fields.Char('Very First origin')
    
    @api.model
    def _run_move_create(self, procurement):
        """give first origin to stock move from procurement"""
        vals = super(procurement_order, self)._run_move_create(procurement)
        vals.update({'first_origin':procurement.first_origin})
        return vals
            
procurement_order()

class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    first_origin = fields.Char('Very First origin')
    
stock_picking()

class stock_move(models.Model):
    _inherit = "stock.move"

    first_origin = fields.Char('Very First origin')
        
    @api.cr_uid_ids_context
    def _picking_assign(self, cr, uid, move_ids, context=None):
        """Try to assign the moves to an existing picking
        that has not been reserved yet and has the same
        procurement group, locations and picking type  (moves should already have them identical)
         Otherwise, create a new picking to assign them to.
        """
        move = self.browse(cr, uid, move_ids, context=context)[0]
        pick_obj = self.pool.get("stock.picking")
        
        if move.picking_type_id.code in ('internal',):
            picks = pick_obj.search(cr, uid, [
                    ('group_id', '=', move.group_id.id),
                    ('location_id', '=', move.location_id.id),
                    ('location_dest_id', '=', move.location_dest_id.id),
                    ('picking_type_id', '=', move.picking_type_id.id),
                    ('first_origin', '=', move.first_origin),
                    ('printed', '=', False),
                    ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])], limit=1, context=context)

        else:
            picks = pick_obj.search(cr, uid, [
                    ('group_id', '=', move.group_id.id),
                    ('location_id', '=', move.location_id.id),
                    ('location_dest_id', '=', move.location_dest_id.id),
                    ('picking_type_id', '=', move.picking_type_id.id),
                    ('printed', '=', False),
                    ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])], limit=1, context=context)
        if picks:
            pick = picks[0]
        else:
            values = self._prepare_picking_assign(cr, uid, move, context=context)
            pick = pick_obj.create(cr, uid, values, context=context)
        return self.write(cr, uid, move_ids, {'picking_id': pick}, context=context)
    
    def _prepare_picking_assign(self, cr, uid, move, context=None):
        values = super(stock_move, self)._prepare_picking_assign(cr, uid, move, context=context)
        values.update({'first_origin':move.picking_id and move.picking_id.name or move.first_origin})
        return values
    
    def _prepare_procurement_from_move(self, cr, uid, move, context=None):
        res = super(stock_move, self)._prepare_procurement_from_move(cr, uid, move, context=context)
        res.update({'first_origin':move.picking_id and move.picking_id.name or move.first_origin})
        return res

stock_move()

class stock_location_path(osv.osv):
    _inherit = 'stock.location.path'
    
    
    def _prepare_push_apply(self, cr, uid, rule, move, context=None):
        res = super(stock_location_path, self)._prepare_push_apply(cr, uid, rule, move, context=context)
        res.update({'first_origin':move.picking_id and move.picking_id.name or move.first_origin})
        return res
        
stock_location_path()

