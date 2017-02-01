
from datetime import date, datetime
from dateutil import relativedelta
import json
import time
import sets
import os
import errno
import openerp
from openerp.osv import fields, osv
from openerp.tools.float_utils import float_compare, float_round
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import SUPERUSER_ID, api, models
import openerp.addons.decimal_precision as dp
from openerp.addons.procurement import procurement
import logging
from openerp.exceptions import UserError
from unidecode import unidecode


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def quick_action_assign(self, cr, uid, ids, context=None):
        """ Check availability of picking moves.
        This has the effect of changing the state and reserve quants on available moves, and may
        also impact the state of the picking as it is computed based on move's states.
        @return: True
        """
        for pick in self.browse(cr, uid, ids, context=context):
            if pick.state == 'draft':
                self.action_confirm(cr, uid, [pick.id], context=context)
            #skip the moves that don't need to be checked
            move_ids = [x.id for x in pick.move_lines if x.state not in ('draft', 'cancel', 'done')]
            if not move_ids:
                raise UserError(_('Nothing to check the availability for.'))
            self.pool.get('stock.move').fast_action_assign(cr, uid, move_ids, context=context)
        return True

    def do_prepare_partial(self, cr, uid, picking_ids, context=None):
        context = context or {}
        pack_operation_obj = self.pool.get('stock.pack.operation')

        #get list of existing operations and delete them
        existing_package_ids = pack_operation_obj.search(cr, uid, [('picking_id', 'in', picking_ids)], context=context)
        if existing_package_ids:
            pack_operation_obj.unlink(cr, uid, existing_package_ids, context)
        for picking in self.browse(cr, uid, picking_ids, context=context):
            forced_qties = {}  # Quantity remaining after calculating reserved quants
            picking_quants = []
            #Calculate packages, reserved quants, qtys of this picking's moves
            for move in picking.move_lines:
                if move.state not in ('assigned', 'confirmed', 'waiting'):
                    continue
                move_quants = move.reserved_quant_ids
                picking_quants += move_quants
                forced_qty = (move.state == 'assigned') and move.product_qty - sum([x.qty for x in move_quants]) or 0
                #if we used force_assign() on the move, or if the move is incoming, forced_qty > 0
                if float_compare(forced_qty, 0, precision_rounding=move.product_id.uom_id.rounding) > 0:
                    if forced_qties.get(move.product_id):
                        forced_qties[move.product_id] += forced_qty
                    else:
                        forced_qties[move.product_id] = forced_qty
            for vals in self._prepare_pack_ops(cr, uid, picking, picking_quants, forced_qties, context=context):
                vals['fresh_record'] = False
                package_id = vals['package_id'] if vals['package_id'] else None
                owner_id = vals['owner_id'] if vals['owner_id'] else None
                ''''
                'pack_lot_ids': [], 'fresh_record': False, 'package_id': False, 'location_dest_id': 9, 
                'product_id': 943, 'product_qty': 1.0, 
                'product_uom_id': 21, 'location_id': 241, 'picking_id': 213597, 'owner_id': False'''
                cr.execute('''
                INSERT INTO stock_pack_operation (id, create_date, create_uid, result_package_id, 
                package_id, product_qty, location_id, 
                qty_done, owner_id, fresh_record, date, product_id, 
                product_uom_id, location_dest_id, picking_id)
                VALUES ((SELECT nextval('stock_pack_operation_id_seq')),NOW() at time zone 'UTC',%s,%s,%s,%s,%s,%s,%s,%s,NOW() at time zone 'UTC',%s,%s,%s,%s)''',
                (uid, package_id, package_id, vals['product_qty'], 
                vals['location_id'], 0, owner_id, vals['fresh_record'], vals['product_id'], vals['product_uom_id'], vals['location_dest_id'], vals['picking_id']))

        self.do_recompute_remaining_quantities(cr, uid, picking_ids, context=context)
        self.write(cr, uid, picking_ids, {'recompute_pack_op': False}, context=context)
        
class StockMove(osv.osv):
    _inherit = "stock.move"

    def fast_action_assign(self, cr, uid, ids, no_prepare=False, context=None):
        """ Checks the product type and accordingly writes the state.
        """
        context = context or {}
        quant_obj = self.pool.get("stock.quant")
        uom_obj = self.pool['product.uom']
        to_assign_moves = set()
        main_domain = {}
        todo_moves = []
        operations = set()
        self.do_unreserve(cr, uid, [x.id for x in self.browse(cr, uid, ids, context=context) if x.reserved_quant_ids and x.state in ['confirmed', 'waiting', 'assigned']], context=context)
        picking = self.browse(cr, uid, ids[0], context)
        for move in self.browse(cr, uid, ids, context=context):
            if move.state not in ('confirmed', 'waiting', 'assigned'):
                continue

            else:
                todo_moves.append(move)

                #we always search for yet unassigned quants
                main_domain[move.id] = [('reservation_id', '=', False), ('qty', '>', 0)]

        # Check all ops and sort them: we want to process first the packages, then operations with lot then the rest
        for move in todo_moves:
            #then if the move isn't totally assigned, try to find quants without any specific domain
            if (move.state != 'assigned') and not context.get("reserve_only_ops"):
                qty_already_assigned = move.reserved_availability
                qty = move.product_qty - qty_already_assigned
                quants = quant_obj.quants_get_preferred_domain(cr, uid, qty, move, domain=main_domain[move.id], preferred_domain_list=[], context=context)
                quant_obj.quants_reserve(cr, uid, quants, move, context=context)
        #force assignation of consumable products and incoming from supplier/inventory/production
        # Do not take force_assign as it would create pack operations
        if to_assign_moves:
            self.write(cr, uid, list(to_assign_moves), {'state': 'assigned'}, context=context)
        if not no_prepare:
            self.check_recompute_pack_op(cr, uid, picking.id, context=context)


