
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
_logger = logging.getLogger(__name__)


class StockMove(osv.osv):
    _inherit = 'stock.move'
    
    def fast_action_done(self, cr, uid, ids, quants, context=None):
        """ Process completely the moves given as ids and if all moves are done, it will finish the picking.
        """
        context = context or {}
        quant_obj = self.pool.get("stock.quant")
        uom_obj = self.pool.get("product.uom")
        todo = [move.id for move in self.browse(cr, uid, ids, context=context) if move.state == "draft"]
        if todo:
            ids = self.action_confirm(cr, uid, todo, context=context)
        procurement_ids = set()
        #Search operations that are linked to the moves
        move_qty = {}
        move_dest_ids = set()
        move_qty[move.id] = move.product_qty
        for move in self.browse(cr, uid, ids, context=context):
            move_qty_cmp = float_compare(move_qty[move.id], 0, precision_rounding=move.product_id.uom_id.rounding)
            if move_qty_cmp > 0:  # (=In case no pack operations in picking)
                main_domain = [('qty', '>', 0)]
                preferred_domain = [('reservation_id', '=', False)]
                preferred_domain_list = [preferred_domain]
#                 self.check_tracking(cr, uid, move, False, context=context)
                qty = move_qty[move.id]
                quants = quant_obj.quants_get_preferred_domain(cr, uid, qty, move, domain=main_domain, preferred_domain_list=preferred_domain_list, context=context)
            quant_obj.quants_move(cr, uid, quants, move, move.location_dest_id, lot_id=move.restrict_lot_id.id, owner_id=move.restrict_partner_id.id, context=context)
#           'success quantsmove'
#              If the move has a destination, add it to the list to reserve
            if move.move_dest_id and move.move_dest_id.state in ('waiting', 'confirmed'):
                move_dest_ids.add(move.move_dest_id.id)

            if move.procurement_id:
                procurement_ids.add(move.procurement_id.id)
#             unreserve the quants and make them available for other operations/moves
            quant_obj.quants_unreserve(cr, uid, move, context=context)
        # Check the packages have been placed in the correct locations
#         self._check_package_from_moves(cr, uid, ids, context=context)
        #set the move as done
        self.write(cr, uid, ids, {'state': 'done', 'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=context)
        #assign destination moves
        if move_dest_ids:
            self.action_assign(cr, uid, list(move_dest_ids), context=context)
        #check picking state to set the date_done is needed
        return True


class stock_inventory(osv.osv):
    _inherit = "stock.inventory"
    _description = "Inventory"

    def fast_prepare_inventory(self, cr, uid, ids, context=None):
        inventory_line_obj = self.pool.get('stock.inventory.line')
        for inventory in self.browse(cr, uid, ids, context=context):
            # If there are inventory lines already (e.g. from import), respect those and set their theoretical qty
            line_ids = [line.id for line in inventory.line_ids]
            if not line_ids and inventory.filter != 'partial':
                #compute the inventory lines and create them
                vals = self._get_inventory_lines(cr, uid, inventory, context=context)
                for product_line in vals:
                    _logger.info ("####### START EXECUTE query 2 #######")
                    cr.execute("INSERT INTO stock_inventory_line (create_date, create_uid, theoretical_qty, product_id, "\
                    "location_id, prod_lot_id, inventory_id, package_id, product_qty, "\
                    "product_uom_id, partner_id) values (NOW() at time zone 'UTC',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (
                        uid, product_line['theoretical_qty'],product_line['product_id'],
                            product_line['location_id'],product_line['prod_lot_id'] or None,
                                product_line['inventory_id'],product_line['package_id'] or None,
                                    product_line['product_qty'],product_line['product_uom_id'],
                                        product_line['partner_id'] or None))
#                     inventory_line_obj.create(cr, uid, product_line, context=context)
                    _logger.info ("####### END EXECUTE query 2 #######")
        _logger.info("get stop inventory")
        _logger.info(datetime.now())
        return self.write(cr, uid, ids, {'state': 'confirm', 'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})

    def fast_action_done(self, cr, uid, ids, context=None):
        """ Finish the inventory"""
        """@return: True
        """
        for inv in self.browse(cr, uid, ids, context=context):
            for inventory_line in inv.line_ids:
                if inventory_line.product_qty < 0 and inventory_line.product_qty != inventory_line.theoretical_qty:
                    raise UserError(_('You cannot set a negative product quantity in an inventory line:\n\t%s - qty: %s') % (inventory_line.product_id.name, inventory_line.product_qty))
            self.action_check(cr, uid, [inv.id], context=context)
            self.write(cr, uid, [inv.id], {'state': 'done'}, context=context)
#             self.post_inventory(cr, uid, inv, context=context)
        return True

class stock_inventory_line(osv.osv):
    _inherit = "stock.inventory.line"

    def _resolve_inventory_line(self, cr, uid, inventory_line, context=None):
        _logger.info("---get start _resolve_inventory_line--")
        _logger.info(datetime.now())
        stock_move_obj = self.pool.get('stock.move')
        quant_obj = self.pool.get('stock.quant')
        diff = inventory_line.theoretical_qty - inventory_line.product_qty
        if not diff:
            return
        #each theorical_lines where difference between theoretical and checked quantities is not 0 is a line for which we need to create a stock move
        vals = {
            'name': _('INV:') + (inventory_line.inventory_id.name or ''),
            'product_id': inventory_line.product_id.id,
            'product_uom': inventory_line.product_uom_id.id,
            'date': inventory_line.inventory_id.date,
            'company_id': inventory_line.inventory_id.company_id.id,
            'inventory_id': inventory_line.inventory_id.id,
            'state': 'confirmed',
            'restrict_lot_id': inventory_line.prod_lot_id.id,
            'restrict_partner_id': inventory_line.partner_id.id,
         }
    
        inventory_location_id = inventory_line.product_id.property_stock_inventory.id
        sign =0 
        location = False
        if diff < 0:
            #found more than expected
            sign = -1
            vals['location_id'] = inventory_location_id
            vals['location_dest_id'] = inventory_line.location_id.id
            vals['product_uom_qty'] = -diff
            location = vals['location_dest_id']
        else:
            #found less than expected
            sign = -1
            vals['location_id'] = inventory_line.location_id.id
            vals['location_dest_id'] = inventory_location_id
            vals['product_uom_qty'] = diff
            location = vals['location_id']
#         move_id = stock_move_obj.create(cr, uid, vals, context=context)
        _logger.info("---get query--")
        _logger.info(datetime.now())
        
        cr.execute("SELECT nextval('stock_move_id_seq')")
        move_id = cr.fetchone()[0]  
#         val = (uid, product_id, 'make_to_stock', \
#                     from_loc, '-', origin, picking_type_id, stock_pick_id, proc_id, group_id, company, 'draft')
        create_date = datetime.now()
        create_uid = uid
        priority = 1
        date_expected = datetime.now()
        product_uom_qty = vals['product_uom_qty']
        product_uom = vals['product_uom']
        date = datetime.now()
        product_id = vals['product_id']
        procure_method = "make_to_stock"
        location_id = vals['location_id']
        location_dest_id = vals['location_dest_id']
        name = vals['name']
        origin = None
        picking_type_id = None
        picking_id = None
        procurement_id = None
        group_id = None
        company_id = vals['company_id']
        state = 'draft'
        restrict_lot_id = vals['restrict_lot_id'] if vals['restrict_lot_id'] else None
        inventory_id = vals['inventory_id']        
        product_qty = vals['product_uom_qty']
        cr.execute("""
            INSERT INTO stock_move(id, create_date, create_uid, priority,
                date_expected, product_uom_qty, product_uom, date, 
                product_id, procure_method, location_id, location_dest_id, 
                name, origin, picking_type_id, picking_id, 
                procurement_id, group_id, company_id, state,
                restrict_lot_id, inventory_id, product_qty )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s)
        """,(move_id, create_date, create_uid, priority, \
             date_expected, abs(product_uom_qty), product_uom, date, \
             product_id, procure_method, location_id, location_dest_id, \
             name, origin, picking_type_id, picking_id, \
             procurement_id, group_id, company_id, state, \
             restrict_lot_id, inventory_id, product_qty))

        move = stock_move_obj.browse(cr, uid, move_id, context=context)
        _logger.info("---get query stop--")
        _logger.info(datetime.now())
        quants = []
        update = False
        if abs(diff) > 0:
            _logger.info("---get start  diff resolve_inventory_line--")
            _logger.info(datetime.now())
            cr.execute(""" 
                SELECT stock_quant.id, stock_quant.qty FROM stock_quant
                WHERE stock_quant.location_id = %s  
                AND  stock_quant.company_id = %s 
                AND  stock_quant.product_id = %s  
                AND stock_quant.qty > 0.0 
                AND  stock_quant.package_id IS NULL  
                AND  stock_quant.lot_id IS NULL  
                AND  stock_quant.owner_id IS NULL
                AND  stock_quant.reservation_id IS NULL 
                ORDER BY stock_quant.in_date ,stock_quant.id
             """, (location, company_id, product_id))
            quant_ids = cr.fetchall()
            _logger.info("---get start  diff2 resolve_inventory_line--")
            _logger.info(datetime.now())
            stock_move_obj.action_done(cr, uid, move_id, context=context)
            quants = [x.id for x in move.quant_ids]
            quant_obj.write(cr, uid, quants, {'package_id': inventory_line.package_id.id}, context=context)
            res = quant_obj.search(cr, uid, [('qty', '<', 0.0), ('product_id', '=', move.product_id.id),
                                    ('location_id', '=', move.location_dest_id.id), ('package_id', '!=', False)], limit=1, context=context)
            if res:
                for quant in move.quant_ids:
                    if quant.location_id.id == move.location_dest_id.id: #To avoid we take a quant that was reconcile already
                        quant_obj._quant_reconcile_negative(cr, uid, quant, move, context=context)
            _logger.info("---get stop  diff2 resolve_inventory_line--")
            _logger.info(datetime.now())
        _logger.info("---get stop _resolve_inventory_line--")
        _logger.info(datetime.now())
        _logger.info(update)
        if not update:
            stock_move_obj.fast_action_done(cr, uid, move_id, quants, context)
        return move_id
