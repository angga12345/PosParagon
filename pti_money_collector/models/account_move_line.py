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

from openerp import models, api, fields
from operator import itemgetter
from openerp.exceptions import RedirectWarning, UserError
from openerp import api, fields, models, _

import logging
_log = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.one
    @api.depends('debit', 'credit')
    def _compute_invoice_id(self):
        
        self._cr.execute('select rel.account_invoice_id from account_invoice_account_move_line_rel rel '\
                        'where rel.account_move_line_id=%s' % self.id)
        res = self._cr.fetchone()
        
        if res:
            self.collector_invoice_id = self.env['account.invoice'].search([('id','=',res[0])])
        else:
            self.collector_invoice_id = False
            
    @api.multi
    def _invoice_id_search(self, operator, operand):
        if operator=='!=' and operand==False:
            self._cr.execute('select distinct(rel.account_move_line_id) from account_invoice_account_move_line_rel rel')
            res = self._cr.fetchall()
            if not res:
                return [('id', '=', '0')]
            else:
                return [('id', 'in', map(itemgetter(0), res))]            
        if operator=='=' and operand==False:
            self._cr.execute('select id from account_move_line '\
                             'where id not in (select distinct(rel.account_move_line_id) '\
                             'from account_invoice_account_move_line_rel rel)')
            res = self._cr.fetchall()
            if not res:
                return [('id', '=', '0')]
            else:
                return [('id', 'in', map(itemgetter(0), res))]

    collector_id = fields.Many2one('res.partner', string='Collector', domain=[('is_collector','=',True)])
    dc_collector_id = fields.Many2one('res.partner', related='collector_id.dc_id', string='DC', store=True, readonly=True)
    collector_invoice_id = fields.Many2one('account.invoice', string='Related Invoice', compute='_compute_invoice_id', search=_invoice_id_search,
        help="It indicate that this journal has relation with invoice and reconciled")
    collector_validated = fields.Boolean(string='Validated')
    

    @api.multi
    def write(self, vals):
        if vals.get('collector_validated', False):
            if not self.collector_invoice_id:
                raise UserError(_('This Line has no related Invoice. You can not continue validate.'))
            collector_name=False
            _log.info (vals.get('collector_id'))
            if vals.get('collector_id',False):
                collector_name = self.env['res.partner'].browse(vals['collector_id']).name
            else:
                if self.collector_id:
                    collector_name = self.collector_id.name
            
            if collector_name:
                make_log = 'Amount %s collected by collector %s ' % (self.credit or self.debit, collector_name)
                self.collector_invoice_id.sudo().message_post(body=make_log)
        if self.collector_validated and not vals.get('collector_validated',False) and self.collector_id:
            make_log = 'Sales Admin change to 0 the amount allocated to collector %s ' % (self.collector_id.name)
            self.collector_invoice_id.sudo().message_post(body=make_log)
            
        result = super(AccountMoveLine, self).write(vals)
        return result

