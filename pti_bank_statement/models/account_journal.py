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


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    ending_date_type = fields.Selection([('last',
                                          'Last Day of The Month'),
                                         ('today', 'Today')],
                                        string="Ending Date Default",
                                        required=True,
                                        default='today')

    show_on_dashboard = \
        fields.Boolean(string='Show journal on dashboard',
                       help="Whether this journal should be "
                       "displayed on the dashboard or not",
                       default=True)

    @api.multi
    def action_open_bank_statement(self):
        obj_account_bank_statement = self.env['account.bank.statement']
        temp = []
        view_id = self.env.ref('account.view_bank_statement_form')
        for data in obj_account_bank_statement.search(
                [('state', 'in', ('open', 'new')),
                 ('journal_id', '=', self.id)]):
            temp.append(data)
        # get record bank of statement which last stack
        res = temp.pop(0)
        journal_id = res.journal_id.id
        if self.type in ['bank', 'cash']:
            action = {
                'name': 'Create cash statement',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id.id,
                'res_id': res.id,
                'context': "{'default_journal_id': " + str(journal_id) + "}",
                'target': 'current',
                'res_model': 'account.bank.statement',
            }
        return action

    @api.model
    def _get_sequence_prefix(self, code, refund=False):
        prefix = code.upper()
        if refund:
            prefix = 'R' + prefix
        return prefix + '/%(range_year)s/%(range_month)s/'

