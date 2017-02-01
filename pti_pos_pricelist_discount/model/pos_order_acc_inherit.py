import time
from datetime import datetime
import openerp
from openerp import tools, SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools import float_is_zero
from openerp.tools.translate import _
from openerp.exceptions import UserError

class pos_order_acc_inherit(osv.osv):
    _inherit = 'pos.order'

    def _payment_fields(self, cr, uid, ui_paymentline, context=None):
        res = super(pos_order_acc_inherit, self)._payment_fields(cr, uid, ui_paymentline, context=context)
        res['traceno'] = ui_paymentline['trace_no'] or 0;
        res['apprcode'] = ui_paymentline['appr_code'] or 0;
        return res;
        
    def _process_order(self, cr, uid, order, context=None):
        res = super(pos_order_acc_inherit, self)._process_order(cr, uid, order, context=context)
        if not float_is_zero(order['amount_return'], self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')):
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
        return res;
