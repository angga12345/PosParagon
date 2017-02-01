from operator import itemgetter
import time
from datetime import date, datetime
import os
import errno
from openerp import api, fields, models, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import ValidationError
from openerp.exceptions import UserError
import logging
_log = logging.getLogger(__name__)
class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Partner'
    user_ids = fields.Many2many('res.users', compute='_compute_user_dc', search='_search_user_dc', string='Related Users')

    @api.multi
    def _credit_debit_get(self):
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        where_params = [tuple(self.ids)] + where_params
        self._cr.execute("""SELECT l.partner_id, act.type, SUM(l.amount_residual)
                      FROM account_move_line l
                      LEFT JOIN account_account a ON (l.account_id=a.id)
                      LEFT JOIN account_account_type act ON (a.user_type_id=act.id)
                      WHERE act.type IN ('receivable','payable')
                      AND l.partner_id IN %s
                      AND l.reconciled IS FALSE
                      """ + where_clause + """
                      GROUP BY l.partner_id, act.type
                      """, where_params)
        for pid, type, val in self._cr.fetchall():
            partner = self.browse(pid)
            if type == 'receivable':
                partner.credit = val
            elif type == 'payable':
                partner.debit = -val

    @api.multi
    def _compute_user_dc(self):
        dc = self[0].dc_id
        self._cr.execute("SELECT id FROM res_users WHERE partner_id = %s", (self[0].id, ))
        user_exist = self._cr.fetchone()
        if user_exist:
            self._cr.execute("SELECT id FROM res_users WHERE partner_id IN (SELECT id FROM res_partner WHERE dc_id = %s)", (self[0].id, ))
            all_users2 = self._cr.fetchall()
            dc.user_ids = [(6, 0, all_users2)]
