from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)
import os
import errno
from unidecode import unidecode

class customer_order(models.Model):
    _inherit = "sale.order"

    @api.multi
    def quick_action_confirm(self):
        context = self._context or False
        if not context.get('checked', False):
            partne_obj = self.env['res.partner']
            MAX_DEPTH = 1
            # this code will handle partner with depth 2 level only
            partner_sudo = partne_obj.sudo().search([('id', '=', self.partner_id.id)])
            list_partner = []
            root = self.searchRoot(partner_sudo, MAX_DEPTH)
            # i decided for child max 1 level depth based on master data customer
            # but if need more we can improve (Keep it simple)
            list_partner.append(root.child_ids)
            list_partner.append(root)
            credit = self.count_all(list_partner)  # count all invoice related with partner
            available_credit = self.partner_id.credit_limit - \
                               self.partner_id.credit - \
                               credit

            if self.amount_total > available_credit:
                title = 'Credit Over Limits!'
                msg = u'Can not confirm the order since the credit balance is %s.' % (available_credit,)
                return self.env['confirm_box'].with_context(sales_order_id=self.id).confirm(title, msg)
            else:
                self.button_dummy()
                self._action_confirm()
        else:
            self.button_dummy()
            self._action_confirm()

    @api.multi
    def _action_confirm(self):
        filename = "/home/logfile/loging_process.txt"
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
                with open('/home/logfile/loging_process.txt', 'a') as file_master:
                    open('/home/logfile/loging_process.txt', 'a')
                    file_master.write('datetime;name;state;function;username' + '\n')
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open('/home/logfile/loging_process.txt', 'a') as file:
            uname = self.env.user.name
            file.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            file.write(';' + self.name + ';' + 'start' + ';' + 'sale_quick_action_confirm ' + ';' + uname + '\n')

        for order in self:
            order.state = 'sale'
            if self.env.context.get('send_email'):
                self.force_quotation_send()
            # create stock.picking
            group_proc = self.env['procurement.group'].create(
                {'name': order.name, 'move_type': order.picking_policy, 'partner_id': order.partner_shipping_id.id})
            order.procurement_group_id = group_proc.id
            order.order_line.prepareDO(group_proc, order)

            if not order.project_id:
                for line in order.order_line:
                    if line.product_id.invoice_policy == 'cost':
                        order._create_analytic_account()
                        break
        if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
            self.action_done()
        stopp = datetime.now()

        with open('/home/logfile/loging_process.txt', 'a') as file:
            uname = self.env.user.name
            file.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            file.write(';' + self.name + ';' + 'stop' + ';' + 'sale_quick_action_confirm ' + ';' + uname + '\n')


class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    def fast_action_confirm(self, cr, uid, ids, context=None):
        filename = "/home/logfile/loging_process.txt"
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
                with open('/home/logfile/loging_process.txt', 'a') as file_master:
                    open('/home/logfile/loging_process.txt', 'a')
                    file_master.write('datetime;name;state;function;username'+'\n')
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open('/home/logfile/loging_process.txt', 'a') as file:
            uname = self.env.user.name
            file.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            file.write(';'+self.name+';' +'start'+';'+ 'picking_quick_action_confirm '+';'+ uname +'\n' ) 

        todo = []
        todo_force_assign = []
        for picking in self.browse(cr, uid, ids, context=context):
            if not picking.move_lines:
                self.launch_packops(cr, uid, [picking.id], context=context)
            if picking.location_id.usage in ('supplier', 'inventory', 'production'):
                todo_force_assign.append(picking.id)
            for r in picking.move_lines:
                if r.state == 'draft':
                    todo.append(r.id)
        if len(todo):
            self.pool.get('stock.move').fast_action_confirm(cr, uid, todo, context=context)

        if todo_force_assign:
            self.force_assign(cr, uid, todo_force_assign, context=context)
        
        with open('/home/logfile/loging_process.txt', 'a') as file:
            uname = self.env.user.name
            file.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            file.write(';'+self.name +';' +'stop'+';'+ 'picking_quick_action_confirm '+';'+ uname +'\n' )

        return True

class StockMove(models.Model):
    _inherit = "stock.move"
    def fast_action_confirm(self, cr, uid, ids, context=None):
        """ Confirms stock move or put it in waiting if it's linked to another move.
        @return: List of ids.
        """
        filename = "/home/logfile/loging_process.txt"
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
                with open('/home/logfile/loging_process.txt', 'a') as file_master:
                    open('/home/logfile/loging_process.txt', 'a')
                    file_master.write('datetime;name;state;function;username'+'\n')
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open('/home/logfile/loging_process.txt', 'a') as file:
            uname = self.env.user.name
            file.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            file.write(';'+unidecode(self.name)+';' +'start'+';'+ 'stock_move_quick_action_confirm '+';'+ uname +'\n' ) 

        if not context:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        states = {
            'confirmed': [],
            'waiting': []
        }
        to_assign = {}
        for move in self.browse(cr, uid, ids, context=context):
            self.attribute_price(cr, uid, move, context=context)
            state = 'confirmed'
            #if the move is preceeded, then it's waiting (if preceeding move is done, then action_assign has been called already and its state is already available)
            if move.move_orig_ids:
                state = 'waiting'
            #if the move is split and some of the ancestor was preceeded, then it's waiting as well
            elif move.split_from:
                move2 = move.split_from
                while move2 and state != 'waiting':
                    if move2.move_orig_ids:
                        state = 'waiting'
                    move2 = move2.split_from
            states[state].append(move.id)
            if not False and move.picking_type_id:
                key = (move.group_id.id, move.location_id.id, move.location_dest_id.id)
                if key not in to_assign:
                    to_assign[key] = []
                to_assign[key].append(move.id)
        moves = [move for move in self.browse(cr, uid, states['confirmed'], context=context) if move.procure_method == 'make_to_order']
        self._create_procurements(cr, uid, moves, context=context)
        for move in moves:
            states['waiting'].append(move.id)
            states['confirmed'].remove(move.id)

        for state, write_ids in states.items():
            if len(write_ids):
                self.write(cr, uid, write_ids, {'state': state}, context=context)
        #assign picking in batch for all confirmed move that share the same details
        for key, move_ids in to_assign.items():
            self._picking_assign(cr, uid, move_ids, context=context)
        moves = self.browse(cr, uid, ids, context=context)
        self._push_apply(cr, uid, moves, context=context)
        with open('/home/logfile/loging_process.txt', 'a') as file:
            uname = self.env.user.name
            file.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            file.write(';'+unidecode(self.name) +';' +'stop'+';'+ 'stock_move_quick_action_confirm '+';'+ uname +'\n' )

        return ids


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def prepareDO(self, group, order):
        filename = "/home/logfile/loging_process.txt"
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
                with open('/home/logfile/loging_process.txt', 'a') as file_master:
                    open('/home/logfile/loging_process.txt', 'a')
                    file_master.write('datetime;name;state;function;username'+'\n')
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open('/home/logfile/loging_process.txt', 'a') as file:
            uname = self.env.user.name
            file.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            file.write(';'+unidecode(self[0].name)+';' +'start'+';'+ 'sale_order_line_quick_action_confirm '+';'+ uname +'\n' ) 

        cr = self._cr
        uid = self._uid

        group_id = group.id
        picking_type = self.env['stock.picking.type'].search([('name','=','Delivery Orders'),('warehouse_id','=',order.warehouse_id.id)])
        proc_order = self.env['procurement.order']
        sm = self.env['stock.move']
        wh_id = order.warehouse_id and order.warehouse_id.id or False
        from_loc = order.warehouse_id.lot_stock_id.id or False
        to_location = order.partner_shipping_id.property_stock_customer.id or False
        origin = order.name
        partner_id = order.partner_shipping_id.id
        picking_type_id = picking_type.id

        company = order.company_id.id
        _logger.info (group_id)
        picking = self.env['stock.picking'].create({
            'partner_id' : partner_id,
            'location_id' : from_loc,
            'location_dest_id' : to_location,
            'origin' : origin,
            'picking_type_id' : picking_type_id,
            'group_id' : group_id,
            })
        stock_pick_id =picking.id
        _logger.info (from_loc)
        _logger.info (to_location)
        for line in self:
            if not line.is_free:
                planned = datetime.strptime(order.date_order, DEFAULT_SERVER_DATETIME_FORMAT)\
                    + timedelta(days=line.customer_lead or 0.0) - timedelta(days=order.company_id.security_lead)

                product_id = line.product_id.id
                product_qty = line.product_uom_qty
                product_uom = line.product_uom.id
                uom_obj = self.pool.get('product.uom')
                res = {}
                quantity = uom_obj._compute_qty_obj(cr, uid, line.product_uom, line.product_uom_qty, line.product_id.uom_id, context=None)

                cr.execute("SELECT nextval('procurement_order_id_seq')")
                proc_id = cr.fetchone()[0]
                cr.execute(
                       """INSERT INTO procurement_order (id, create_date, write_date, create_uid, write_uid,
                           name, origin, date_planned, product_id, product_qty, product_uom, company_id, sale_line_id, location_id,
                           warehouse_id, partner_dest_id,priority,rule_id,group_id, state)
                           VALUES (%s,NOW() at time zone 'UTC',NOW() at time zone 'UTC',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (
                               proc_id, uid, uid, line.name, origin, planned, product_id, product_qty, product_uom, company, line.id, from_loc, wh_id, to_location, 1, 4366, group_id, 'running'))
                val = (uid, planned, to_location, product_qty, quantity, product_uom, planned, product_id, 'make_to_stock', \
                    from_loc, '-', origin, picking_type_id, stock_pick_id, proc_id, group_id, company, 'draft')
                cr.execute("""
                    INSERT INTO stock_move(id, create_date, create_uid, priority,
                        date_expected, location_dest_id, product_uom_qty, product_qty, product_uom, date, product_id, procure_method,
                        location_id, name, origin, picking_type_id, picking_id, procurement_id, group_id, company_id, state )
                    VALUES ((SELECT nextval('stock_move_id_seq')),NOW() at time zone 'UTC', %s, 1,
                        %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, val)

        picking.action_confirm()
        with open('/home/logfile/loging_process.txt', 'a') as file:
            uname = self.env.user.name
            file.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            file.write(';'+unidecode(self[0].name) +';' +'stop'+';'+ 'sale_order_line_quick_action_confirm '+';'+ uname +'\n' )
