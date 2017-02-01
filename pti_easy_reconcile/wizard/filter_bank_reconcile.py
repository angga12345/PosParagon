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

from openerp import models, fields, api
from openerp.exceptions import ValidationError

import logging
_log = logging.getLogger(__name__)
class FilterBankReconcile(models.TransientModel):
    _name = 'filter.bank.reconcile'
    
    use_filter = fields.Boolean("Use Filter")
    partner_id = fields.Many2one('res.partner','Partner')
    memo = fields.Char(string='Memo')
    
    @api.multi
    def action_filter_bank_reconcile(self):
        imd = self.env['ir.model.data']
        absl = self.env['account.bank.statement.line']
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        statement_ids = [active_id]
        statement_line_ids = []
        if self.use_filter:
            _log.info ("active_id %s " % active_id)
            domain =[('statement_id','=',active_id)]
            if self.partner_id:
                domain.append(('partner_id','=',self.partner_id.id))
            if self.memo:
                domain.append(('name','like','%'+self.memo+'%'))
            line_ids = absl.search(domain)
            for l in line_ids:
                statement_line_ids.append(l.id)
            
        ctx = {
            'statement_ids': statement_ids,
            'statement_line_ids': statement_line_ids,
        }
        
        _log.info (ctx)
        action_rec = imd.xmlid_to_object('account.action_bank_reconcile_bank_statements')
        if action_rec:
            action = action_rec.read([])[0]
            action['context'] = ctx
            return action

