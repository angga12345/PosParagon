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

from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError
import logging
_log = logging.getLogger(__name__)
class AccountMove(models.Model):
    _inherit = "account.move"
    
    
    @api.multi
    def reverse_moves(self, date=None, journal_id=None):
        """override this function..
        because I need to add context on copy line 
        ac_move.copy
        to be
        ac_move.with_context(dont_create_taxes=True).copy
        """
        date = date or fields.Date.today()
        reversed_moves = self.env['account.move']
        for ac_move in self:
            reversed_move = ac_move.with_context(dont_create_taxes=True).copy(default={'date': date,
                'journal_id': journal_id.id if journal_id else ac_move.journal_id.id,
                'ref': _('reversal of: ') + ac_move.name})
            for acm_line in reversed_move.line_ids:
                acm_line.with_context(check_move_validity=False).write({
                    'debit': acm_line.credit,
                    'credit': acm_line.debit,
                    'amount_currency': -acm_line.amount_currency
                    })
            reversed_moves |= reversed_move
        if reversed_moves:
            reversed_moves._post_validate()
            reversed_moves.post()
            return [x.id for x in reversed_moves]
        return []
    
    @api.multi
    def correct_moves(self, date=None, journal_id=None, partner_id=None):
        #unreconcile
        for ac_move in self:
            ac_move.line_ids.remove_move_reconcile()
        #reverse
        reversed_moves = self.reverse_moves(date, journal_id)
        #Reconcile the initial transaction with the reversal.
        to_be_reconciled = []
        for ac_move in self:
            for aml in ac_move.line_ids:
                if aml.account_id.reconcile:
                    to_be_reconciled.append(aml.id)
        for ac_move in self.env['account.move'].browse(reversed_moves):
            for aml in ac_move.line_ids:
                if aml.account_id.reconcile:
                    to_be_reconciled.append(aml.id)
        if len(to_be_reconciled):
            move_lines = self.env['account.move.line'].browse(to_be_reconciled)
            move_lines.reconcile()
            
        #duplicate
        date = date or fields.Date.today()
        corrected_moves = self.env['account.move']
        rec_move_ids = self.env['account.partial.reconcile']

        for ac_move in self:
            if not partner_id:
                corrected_move = ac_move.with_context(dont_create_taxes=True).copy(default={'date': date,
                    'journal_id': journal_id.id if journal_id else ac_move.journal_id.id,
                    'ref': _('corrected of: ') + ac_move.name})
                for acm_line in corrected_move.line_ids:
                    acm_line.with_context(check_move_validity=False).write({
                        'name': acm_line.name+" corrected",
                        })
                corrected_moves |= corrected_move
            else:
                corrected_move = ac_move.with_context(dont_create_taxes=True).copy(default={'date': date,
                    'journal_id': journal_id.id if journal_id else ac_move.journal_id.id,
                    'ref': _('corrected of: ') + ac_move.name,
                    'partner_id': partner_id.id,
                    'dc_id': partner_id.dc_id.id,
                    })
                for acm_line in corrected_move.line_ids:
                    acm_line.with_context(check_move_validity=False).write({
                        'name': acm_line.name+" corrected",
                        'partner_id': partner_id.id,
                        })
                corrected_moves |= corrected_move
        if corrected_moves:
            return reversed_moves + [x.id for x in corrected_moves]
        return True
    

