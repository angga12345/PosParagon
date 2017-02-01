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

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError

class CollectorBonusReport(models.TransientModel):
    _name = 'collector.bonus.report'
    
    use_filter = fields.Boolean(string='Filter by Date')
    date_from = fields.Date(string='Date From',default=fields.Date.context_today)
    date_to = fields.Date(string='Date To',default=fields.Date.context_today)

    @api.multi
    def action_show_collector_lines(self):
        collector_id = self._context['active_id']
        collector_line_obj = self.env['account.move.line']
        collector_lines = []
        if self.use_filter:
            collector_lines = collector_line_obj.search(
                [('collector_id', '=', collector_id),
                 ('move_id.state','=','posted'),
                 ('collector_validated','=',True),
                 ('date','>=',self.date_from),
                 ('date','<=',self.date_to),
                ])
        else:
            collector_lines = collector_line_obj.search(
                [('collector_id', '=', collector_id),
                 ('move_id.state','=','posted'),
                 ('collector_validated','=',True),
                ])
        
        if len(collector_lines)>0:
            line_ids = []
            for line in collector_lines:
                line_ids.append(line.id)
                
            list_view_id = self.env.ref('pti_money_collector.view_move_line_collector_tree')
            imd = self.env['ir.model.data']
            action = imd.xmlid_to_object('pti_money_collector.action_move_line_collector')
    
            result = {
                'name': action.name,
                'help': action.help,
                'type': action.type,
                'views': [[list_view_id.id, 'tree']],
                'target': action.target,
                'res_model': action.res_model,
                'domain': "[('id','in',%s)]" % line_ids
            }
            return result
        else:
            raise UserError(_('No Transaction Lines avalaible.'))
        

