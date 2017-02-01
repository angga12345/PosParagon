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
from openerp.tools.translate import _

class AccountMoveCorrection(models.TransientModel):
    """
    Account move correction wizard, it cancel an account move by reversing it.
    """
    _name = 'account.move.correction'
    _description = 'Account move correction'

    date = fields.Date(string='Correction Date', default=fields.Date.context_today, required=True)
    journal_id = fields.Many2one('account.journal', string='Use Specific Journal', help='If empty, uses the journal of the journal entry to be reversed.')
    partner_id = fields.Many2one('res.partner', string='New Partner', help='If empty, it will not change initial partner.')

    @api.multi
    def reverse_moves(self):
        ac_move_ids = self._context.get('active_ids', False)
        res = self.env['account.move'].browse(ac_move_ids).correct_moves(self.date, self.journal_id or False, self.partner_id or False)
        if res:
            return {
                'name': _('Corrected Moves'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'domain': [('id', 'in', res)],
            }
        return {'type': 'ir.actions.act_window_close'}

