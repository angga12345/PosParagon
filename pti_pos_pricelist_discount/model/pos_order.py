import time
from datetime import datetime
import openerp
from openerp import tools, SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools import float_is_zero
from openerp.tools.translate import _
from openerp.exceptions import UserError

class pos_order_extend(osv.osv):
    _inherit = 'pos.order'

    def _payment_fields(self, cr, uid, ui_paymentline, context=None):
        return {
            'amount':       ui_paymentline['amount'] or 0.0,
            'batchno': ui_paymentline['batchno'] or 0,
            'traceno': ui_paymentline.get('traceno', 0),
            'apprcode': ui_paymentline.get('apprcode',0),
            'payment_date': ui_paymentline['name'],
            'statement_id': ui_paymentline['statement_id'],
            'payment_name': ui_paymentline.get('note',False),
            'journal':      ui_paymentline['journal_id'],
        }
        
    def _process_order(self, cr, uid, order, context=None):
        session = self.pool.get('pos.session').browse(cr, uid, order['pos_session_id'], context=context)

        if session.state == 'closing_control' or session.state == 'closed':
            session_id = self._get_valid_session(cr, uid, order, context=context)
            session = self.pool.get('pos.session').browse(cr, uid, session_id, context=context)
            order['pos_session_id'] = session_id
#         self._set_price_unit(order['lines'], order)
        order_id = self.create(cr, uid, self._order_fields(cr, uid, order, context=context),context)

        journal_ids = set()
        for payments in order['statement_ids']:
            self.add_payment(cr, uid, order_id, self._payment_fields(cr, uid, payments[2], context=context), context=context)
            journal_ids.add(payments[2]['journal_id'])
           
        if session.sequence_number <= order['sequence_number']:
            session.write({'sequence_number': order['sequence_number'] + 1})
            session.refresh()

        if not float_is_zero(order['amount_return'], self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')):
            cash_journal = session.cash_journal_id.id
            if not cash_journal:
                # Select for change one of the cash journals used in this payment
                cash_journal_ids = self.pool['account.journal'].search(cr, uid, [
                    ('type', '=', 'cash'),
                    ('id', 'in', list(journal_ids)),
                ], limit=1, context=context)
                if not cash_journal_ids:
                    # If none, select for change one of the cash journals of the POS
                    # This is used for example when a customer pays by credit card
                    # an amount higher than total amount of the order and gets cash back
                    cash_journal_ids = [statement.journal_id.id for statement in session.statement_ids
                                        if statement.journal_id.type == 'cash']
                    if not cash_journal_ids:
                        raise UserError(_("No cash statement found for this session. Unable to record returned cash."))
                cash_journal = cash_journal_ids[0]
            
            batch_number = 0 
            trace_no = 0
            appr_code = 0
            
            for paymentline in order['statement_ids']:
                if(paymentline[2]['amount']==order['amount_return']):
                    batch_number = paymentline[2]['batchno']
                    trace_no = paymentline[2]['traceno']
                    appr_code = paymentline[2]['apprcode']
            
                
            self.add_payment(cr, uid, order_id, {
                'amount': -order['amount_return'],
                'batchno' : batch_number,
                'traceno': trace_no,
                'apprcode': appr_code,
                'payment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'payment_name': _('return'),
                'journal': cash_journal,
            }, context=context)
        return order_id
    
    def add_payment(self, cr, uid, order_id, data, context=None):
            """Create a new payment for the order"""
            context = dict(context or {})
            statement_line_obj = self.pool.get('account.bank.statement.line')
            property_obj = self.pool.get('ir.property')
            order = self.browse(cr, uid, order_id, context=context)
            date = data.get('payment_date', time.strftime('%Y-%m-%d'))
            if len(date) > 10:
                timestamp = datetime.strptime(date, tools.DEFAULT_SERVER_DATETIME_FORMAT)
                ts = fields.datetime.context_timestamp(cr, uid, timestamp, context)
                date = ts.strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
            
            args = {
                'amount': data['amount'],
                'batch_number': data['batchno'],
                'trace_no': data['traceno'],
                'appr_code': data['apprcode'],
                'date': date,
                'name': order.name + ': ' + (data.get('payment_name', '') or ''),
                'partner_id': order.partner_id and self.pool.get("res.partner")._find_accounting_partner(order.partner_id).id or False,
            }

            journal_id = data.get('journal', False)
            statement_id = data.get('statement_id', False)
            assert journal_id or statement_id, "No statement_id or journal_id passed to the method!"

            journal = self.pool['account.journal'].browse(cr, uid, journal_id, context=context)
            # use the company of the journal and not of the current user
            company_cxt = dict(context, force_company=journal.company_id.id)
            account_def = property_obj.get(cr, uid, 'property_account_receivable_id', 'res.partner', context=company_cxt)
            args['account_id'] = (order.partner_id and order.partner_id.property_account_receivable_id \
                                 and order.partner_id.property_account_receivable_id.id) or (account_def and account_def.id) or False

            if not args['account_id']:
                if not args['partner_id']:
                    msg = _('There is no receivable account defined to make payment.')
                else:
                    msg = _('There is no receivable account defined to make payment for the partner: "%s" (id:%d).') % (order.partner_id.name, order.partner_id.id,)
                raise UserError(msg)

            context.pop('pos_session_id', False)

            for statement in order.session_id.statement_ids:
                if statement.id == statement_id:
                    journal_id = statement.journal_id.id
                    break
                elif statement.journal_id.id == journal_id:
                    statement_id = statement.id
                    break

            if not statement_id:
                raise UserError(_('You have to open at least one cashbox.'))

            args.update({
                'statement_id': statement_id,
                'pos_statement_id': order_id,
                'journal_id': journal_id,
                'ref': order.session_id.name,
            })

            statement_line_obj.create(cr, uid, args, context=context)

            return statement_id