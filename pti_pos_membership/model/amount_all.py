import logging
import time
from datetime import datetime
import uuid
import sets
import math

from functools import partial

import openerp
import openerp.addons.decimal_precision as dp
from openerp import tools, models, SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools import float_is_zero
from openerp.tools.translate import _
from openerp.exceptions import UserError


_logger = logging.getLogger(__name__)

class pos_order_line(osv.osv):
    _inherit = "pos.order.line"
    
        
    def _amount_line_all(self, cr, uid, ids, field_names, arg, context=None):
        res = dict([(i, {}) for i in ids])
        account_tax_obj = self.pool.get('account.tax')
        for line in self.browse(cr, uid, ids, context=context):
            cur = line.order_id.pricelist_id.currency_id
            taxes = [ tax for tax in line.tax_ids if tax.company_id.id == line.order_id.company_id.id ]
            fiscal_position_id = line.order_id.fiscal_position_id
            if fiscal_position_id:
                taxes = fiscal_position_id.map_tax(taxes)
            taxes_ids = [ tax.id for tax in taxes ]
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            res[line.id]['price_subtotal'] = res[line.id]['price_subtotal_incl'] = price * line.qty
            if taxes_ids:
                taxes = account_tax_obj.browse(cr, uid, taxes_ids, context).compute_all(price, cur, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
                res[line.id]['price_subtotal'] = round(taxes['total_excluded'])
                res[line.id]['price_subtotal_incl'] = round(taxes['total_included'])
        return res
    
    _columns = {
        'price_subtotal': fields.function(_amount_line_all, multi='pos_order_line_amount', digits=0, string='Subtotal w/o Tax'),
        'price_subtotal_incl': fields.function(_amount_line_all, multi='pos_order_line_amount', digits=0, string='Subtotal'),
        'reward_id': fields.many2one('loyalty.reward', 'Loyalty reward id'),
        'reward_gift_id': fields.many2one('product.product', 'Gift reward id')
    }
    
class pos_order(osv.osv):
    _inherit = "pos.order"
    
    
    def _create_account_move_line(self, cr, uid, ids, session=None, move_id=None, context=None):
        # Tricky, via the workflow, we only have one id in the ids variable
        """Create a account move line of order grouped by products or not."""
        account_move_obj = self.pool.get('account.move')
        account_tax_obj = self.pool.get('account.tax')
        property_obj = self.pool.get('ir.property')
        cur_obj = self.pool.get('res.currency')

        #session_ids = set(order.session_id for order in self.browse(cr, uid, ids, context=context))

        if session and not all(session.id == order.session_id.id for order in self.browse(cr, uid, ids, context=context)):
            raise UserError(_('Selected orders do not have the same session!'))

        grouped_data = {}
        have_to_group_by = session and session.config_id.group_by or False

        for order in self.browse(cr, uid, ids, context=context):
            if order.account_move:
                continue
            if order.state != 'paid':
                continue

            current_company = order.sale_journal.company_id
            rel_kateg = order.rel_cat_shop

            group_tax = {}
            account_def = property_obj.get(cr, uid, 'property_account_receivable_id', 'res.partner', context=context)

            order_account = order.partner_id and \
                            order.partner_id.property_account_receivable_id and \
                            order.partner_id.property_account_receivable_id.id or \
                            account_def and account_def.id

            if move_id is None:
                
                if rel_kateg == '':
                    
                    # Create an entry for the sale
                    move_id = self._create_account_move(cr, uid, order.session_id.start_at, order.name, order.sale_journal.id, order.company_id.id, context=context)

            move = account_move_obj.browse(cr, SUPERUSER_ID, move_id, context=context)

            def insert_data(data_type, values):
                # if have_to_group_by:

                sale_journal_id = order.sale_journal.id

                # 'quantity': line.qty,
                # 'product_id': line.product_id.id,
                values.update({
                    'ref': order.name,
                    'partner_id': order.partner_id and self.pool.get("res.partner")._find_accounting_partner(order.partner_id).id or False,
                    'journal_id' : sale_journal_id,
                    'date' : fields.date.context_today(self, cr, uid, context=context),
                    'move_id' : move_id,
                    'company_id': current_company.id,
                })

                if data_type == 'product':
                    key = ('product', values['partner_id'], (values['product_id'], values['name']), values['analytic_account_id'], values['debit'] > 0)
                elif data_type == 'tax':
                    key = ('tax', values['partner_id'], values['tax_line_id'], values['debit'] > 0)
                elif data_type == 'counter_part':
                    key = ('counter_part', values['partner_id'], values['account_id'], values['debit'] > 0)
                else:
                    return

                grouped_data.setdefault(key, [])

                # if not have_to_group_by or (not grouped_data[key]):
                #     grouped_data[key].append(values)
                # else:
                #     pass

                if have_to_group_by:
                    if not grouped_data[key]:
                        grouped_data[key].append(values)
                    else:
                        for line in grouped_data[key]:
                            if line.get('tax_code_id') == values.get('tax_code_id'):
                                current_value = line
                                current_value['quantity'] = current_value.get('quantity', 0.0) +  values.get('quantity', 0.0)
                                current_value['credit'] = current_value.get('credit', 0.0) + values.get('credit', 0.0)
                                current_value['debit'] = current_value.get('debit', 0.0) + values.get('debit', 0.0)
                                break
                        else:
                            grouped_data[key].append(values)
                else:
                    grouped_data[key].append(values)

            #because of the weird way the pos order is written, we need to make sure there is at least one line, 
            #because just after the 'for' loop there are references to 'line' and 'income_account' variables (that 
            #are set inside the for loop)
            #TOFIX: a deep refactoring of this method (and class!) is needed in order to get rid of this stupid hack
            assert order.lines, _('The POS order must have lines when calling this method')
            # Create an move for each order line
            
            cur = order.pricelist_id.currency_id
            
            #get membership global disc value
            res={}
            res[order.id] = {
                'membership_global_disc': order.membership_global_disc,
            }
            
            membership_disc_global = res[order.id]['membership_global_disc']
            
            for line in order.lines:
                #amount untaxed included membership disc global
                amount = line.price_subtotal - (line.price_subtotal * (membership_disc_global / 100 ))

                # Search for the income account
                if  line.product_id.property_account_income_id.id:
                    income_account = line.product_id.property_account_income_id.id
                elif line.product_id.categ_id.property_account_income_categ_id.id:
                    income_account = line.product_id.categ_id.property_account_income_categ_id.id
                else:
                    raise UserError(_('Please define income '\
                        'account for this product: "%s" (id:%d).') \
                        % (line.product_id.name, line.product_id.id))

                name = line.product_id.name
                if line.notice:
                    # add discount reason in move
                    name = name + ' (' + line.notice + ')'

                # Create a move for the line for the order line
                insert_data('product', {
                    'name': name,
                    'quantity': line.qty,
                    'product_id': line.product_id.id,
                    'account_id': income_account,
                    'analytic_account_id': self._prepare_analytic_account(cr, uid, line, context=context),
                    'credit': ((amount>0) and amount) or 0.0,
                    'debit': ((amount<0) and -amount) or 0.0,
                    'partner_id': order.partner_id and self.pool.get("res.partner")._find_accounting_partner(order.partner_id).id or False
                })
                # Create the tax lines
                taxes = []
                for t in line.tax_ids_after_fiscal_position:
                    if t.company_id.id == current_company.id:
                        taxes.append(t.id)
                if not taxes:
                    continue
                for tax in account_tax_obj.browse(cr,uid, taxes, context=context).compute_all(line.price_unit * (100.0-line.discount) / 100.0, cur, line.qty)['taxes']:
                    insert_data('tax', {
                        'name': _('Tax') + ' ' + tax['name'],
                        'product_id': line.product_id.id,
                        'quantity': line.qty,
                        'account_id': tax['account_id'] or income_account,
                        'credit': ((round(tax['amount'])>0) and round(tax['amount'])) or 0.0,
                        'debit': ((round(tax['amount'])<0) and -round(tax['amount'])) or 0.0,
                        'tax_line_id': tax['id'],
                        'partner_id': order.partner_id and self.pool.get("res.partner")._find_accounting_partner(order.partner_id).id or False
                    })

            # counterpart
            insert_data('counter_part', {
                'name': _("Trade Receivables"), #order.name,
                'account_id': order_account,
                'credit': ((order.amount_total < 0) and -order.amount_total) or 0.0,
                'debit': ((order.amount_total > 0) and order.amount_total) or 0.0,
                'partner_id': order.partner_id and self.pool.get("res.partner")._find_accounting_partner(order.partner_id).id or False
            })

            
            order.write({'state':'done'})

        all_lines = []
        for group_key, group_data in grouped_data.iteritems():
            for value in group_data:
                all_lines.append((0, 0, value),)
        
        if move_id:
            
            if rel_kateg == '':
                self.pool.get("account.move").write(cr, SUPERUSER_ID, [move_id], {'line_ids':all_lines}, context=context)
                self.pool.get("account.move").post(cr, SUPERUSER_ID, [move_id], context=context)

        return True
    
    #menyimpan nilai order fields dari JS langsung ke Pyton lalu ke database
    def _order_fields(self, cr, uid, ui_order, context=None):
        process_line = partial(self.pool['pos.order.line']._order_line_fields, cr, uid, context=context)
        #print "shop identifier period: ",ui_order['pos_order_shop_identifier_period']
        shop_identifier_period = shop_identifier_origin = ""
        
        if ui_order.get('pos_order_shop_identifier_period') and ui_order.get('pos_order_shop_identifier_origin'):
            shop_identifier_period = ui_order.get('pos_order_shop_identifier_period', "")
            shop_identifier_origin = ""
        elif ui_order.get('pos_order_shop_identifier_origin') and not ui_order.get('pos_order_shop_identifier_period'):
            shop_identifier_origin = ui_order.get('pos_order_shop_identifier_origin', "")
            shop_identifier_period = ""
        elif not ui_order.get('pos_order_shop_identifier_origin') and not ui_order.get('pos_order_shop_identifier_period'):
            shop_identifier_origin = ""
            shop_identifier_period = ""
        elif not ui_order.get('pos_order_shop_identifier_origin') and ui_order.get('pos_order_shop_identifier_period'):
            shop_identifier_period = ui_order.get('pos_order_shop_identifier_period', "")
            shop_identifier_origin = ""
            
        return {
            'name':         ui_order['name'],
            'user_id':      ui_order['user_id'] or False,
            'session_id':   ui_order['pos_session_id'],
            'lines':        [process_line(l) for l in ui_order['lines']] if ui_order['lines'] else False,
            'pos_reference':ui_order['name'],
            'partner_id':   ui_order['partner_id'] or False,
            'date_order':   ui_order['creation_date'],
            'fiscal_position_id': ui_order['fiscal_position_id'],
            'shop_identifier_period': shop_identifier_period,
            'shop_identifier_origin': shop_identifier_origin,
            'amount_total': ui_order['amount_total'],
            'loyalty_reward_id': ui_order.get('loyalty_reward_id')
        }
    
    def create_from_ui(self, cr, uid, orders, context=None):
        # Keep only new orders
        submitted_references = [o['data']['name'] for o in orders]
        test = [o['data'] for o in orders]
        
        existing_order_ids = self.search(cr, uid, [('pos_reference', 'in', submitted_references)], context=context)
        existing_orders = self.read(cr, uid, existing_order_ids, ['pos_reference'], context=context)
        existing_references = set([o['pos_reference'] for o in existing_orders])
        orders_to_save = [o for o in orders if o['data']['name'] not in existing_references]
 
        order_ids = []
 
        for tmp_order in orders_to_save:
            to_invoice = tmp_order['to_invoice']
            order = tmp_order['data']
            order_id = self._process_order(cr, uid, order, context=context)
            order_ids.append(order_id)
 
            try:
                self.signal_workflow(cr, uid, [order_id], 'paid')
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))
 
            if to_invoice:
                self.action_invoice(cr, uid, [order_id], context)
                order_obj = self.browse(cr, uid, order_id, context)
                self.pool['account.invoice'].signal_workflow(cr, SUPERUSER_ID, [order_obj.invoice_id.id], 'invoice_open')
 
        return order_ids
    
    def _amount_all(self, cr, uid, ids, name, args, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_paid': 0.0,
                'amount_return':0.0,
                'amount_tax':0.0,
                'membership_global_disc': 0.0,
            }
            
            val1 = val2 = 0.0
            cur = order.pricelist_id.currency_id
            res[order.id]['membership_global_disc'] = cur_obj.round(cr, uid, cur, order.membership_global_disc)
            for payment in order.statement_ids:
                res[order.id]['amount_paid'] +=  payment.amount
                res[order.id]['amount_return'] += (payment.amount < 0 and payment.amount or 0)
            for line in order.lines:
                val1 += self._amount_line_tax(cr, uid, line, order.fiscal_position_id, context=context)
                val2 += line.price_subtotal
            res[order.id]['amount_tax'] = round(cur_obj.round(cr, uid, cur, val1))
            amount_md = res[order.id]['membership_global_disc'] / 100 
            
            amount_afterdisctax = val2 - (val2 * cur_obj.round(cr, uid, cur, amount_md))
            amount_untaxed = cur_obj.round(cr, uid, cur, amount_afterdisctax)#cur_obj.round(cr, uid, cur, amount_afterdisctax)
            res[order.id]['amount_total'] = round(res[order.id]['amount_tax'] + amount_untaxed)

           
        return res
    
    
    
    
    _columns = {
    'membership_global_disc': fields.related('partner_id', 'disc_percentage', string="Membership Discount Global", type='float'),
    'amount_tax': fields.function(_amount_all, string='Taxes', digits=0, multi='all'),
    'amount_total': fields.function(_amount_all, string='Total', digits=0,  multi='all'),
    'amount_paid': fields.function(_amount_all, string='Paid', states={'draft': [('readonly', False)]}, readonly=True, digits=0, multi='all'),
    'amount_return': fields.function(_amount_all, string='Returned', digits=0, multi='all'),
    }
    
    