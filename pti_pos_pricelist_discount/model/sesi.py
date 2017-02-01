import logging
import time
from datetime import datetime
import uuid
import sets

from functools import partial

import openerp
import openerp.addons.decimal_precision as dp
from openerp import tools, models, SUPERUSER_ID, api
from openerp.osv import fields, osv
from openerp.tools import float_is_zero
from openerp.tools.translate import _
from openerp.exceptions import UserError


_logger = logging.getLogger(__name__)

class pos_config(osv.osv):
    _inherit = 'pos.config'

    _columns = {
        'stock_location_id': fields.many2one('stock.location', 'Stock Location', domain=[('usage', '=', 'internal')])
    }

    # remove default value
    _defaults = {
        'stock_location_id': False
    }

    def open_session_cb(self, cr, uid, ids, context=None):
        assert len(ids) == 1, "you can open only one session at a time"

        proxy = self.pool.get('pos.session')
        record = self.browse(cr, uid, ids[0], context=context)
        current_session_id = record.current_session_id
        if not current_session_id:
            values = {
                'user_id': uid,
                'config_id': record.id,
                'categ_shop': record.cat_store_text, #kategori shop
            }
            session_id = proxy.create(cr, uid, values, context=context)
            self.write(cr, SUPERUSER_ID, record.id, {'current_session_id': session_id}, context=context)
            if record.current_session_id.state == 'opened':
                return self.open_ui(cr, uid, ids, context=context)
            return self._open_session(session_id)
        return self._open_session(current_session_id.id)

class pos_session(osv.osv):
    _inherit = 'pos.session'
     

    def create(self, cr, uid, values, context=None):
        res = super(pos_session, self).create(cr, uid, values, context=context)
        kategori = values.get('categ_shop')

        for possesi_ids in self.browse(cr, uid, res, context=context):
            for accountbankstate_ids in possesi_ids.statement_ids:
                accountbankstate_ids.kategori_shop = kategori

        return res

    def _confirm_orders(self, cr, uid, ids, context=None):
        pos_order_obj = self.pool.get('pos.order')
        for session in self.browse(cr, uid, ids, context=context):
            company_id = session.config_id.journal_id.company_id.id
            local_context = dict(context or {}, force_company=company_id)
            order_ids = [order.id for order in session.order_ids if order.state == 'paid']

            #move_id = pos_order_obj._create_account_move(cr, uid, session.start_at, session.name, session.config_id.journal_id.id, company_id, context=context)
            
            pos_order_obj._create_account_move_line(cr, uid, order_ids, session, move_id=None, context=local_context)

            for order in session.order_ids:
                if order.state == 'done':
                    continue
                if order.state not in ('paid', 'invoiced'):
                    raise UserError(_("You cannot confirm all orders of this session, because they have not the 'paid' status"))
                else:
                    pos_order_obj.signal_workflow(cr, uid, [order.id], 'done')

        return True
