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
from openerp.exceptions import ValidationError
import datetime
import calendar


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'
        
    @api.one
    def _groups_access(self):
        allow = False
        access = [
                     {'module' : 'pti_branch', 'group_id' : 'group_pti_branch_finance_admin'}
                    ]
        ir_model_data = self.env['ir.model.data']
        array_group = []
        for data in access:
            id_group = ir_model_data.get_object_reference(data['module'], data['group_id'])[1]
            if id_group:
                array_group.append(id_group)

        user = self.env.user
        group_ids = tuple(array_group)
 
        for group in user.groups_id:
            if group.id in group_ids:
                allow = True
                break

        self.access_group = allow

    @api.model
    def _default_starting_date(self):
        journal_id = (self._context.get('default_journal_id', False)
                      or self._context.get('journal_id', False))
        if journal_id:
            last_bnk_stmt = self.search([('journal_id', '=', journal_id)],
                                        order="date_done desc",
                                        limit=1)
            if last_bnk_stmt:
                return last_bnk_stmt.start_date
            else:
                return datetime.datetime.now()
        else:
            return datetime.datetime.now()

    start_date = fields.Date('Starting Date', required=True,
                             default=_default_starting_date)

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        journal_id = self.journal_id.id
        cr = self._cr
        result = cr.execute('SELECT max(date) as date '\
                            'FROM account_bank_statement '\
                            'WHERE journal_id = %s',
                            [(journal_id)])
        result = self.env.cr.dictfetchall()
        date = result[0]['date']

        if not date:
            self.start_date = datetime.datetime.now()
        else:
            self.start_date = date

        if self.journal_id.ending_date_type == 'last':
            year = datetime.datetime.now().year
            month = datetime.datetime.now().month
            day = calendar.monthrange(year, month)[1]
            self.date = datetime.date(year, month, day)

    @api.onchange('line_ids')
    def _onchange_amount(self):
        self.balance_end_real = self.balance_end

    @api.constrains('start_date', 'date')
    def _check_date(self):
        if self.start_date > self.date:
            raise ValidationError('Ending Date must be equal or greater\
                than Starting Date')
        else:
            cr = self._cr
            result = cr.execute('SELECT max(date) as date '\
                                'FROM account_bank_statement '\
                                'WHERE journal_id = %s and '\
                                'id != %s',
                                [(self.journal_id.id), (self.id)])
            result = self.env.cr.dictfetchall()
#             if len(result) == 0:
#                 pass
#             else:
#                 ending_date = result[0]['date']
#                 if self.start_date < ending_date:
#                     raise ValidationError('Starting Date must be or equal\
#                     to Ending Date in the last Bank Statement')

    @api.constrains('balance_start', 'balance_end_real')
    def _check_balance(self):
        result = self._get_prev_bnk_stmt()
        if len(result) == 0:
            pass
        else:
            current_id = result[0]['id']
            bnk_statements = self.search([('id', '=', current_id)])
#remove the check starting balance meanwhile we fix it            
#            if self.balance_start != bnk_statements.balance_end_real:
#                raise ValidationError(_('Starting Balance must be equal\
#                     to Ending Balance in the last Bank Statement,\
#                     \nEnding Balance in last Bank Statement %s is %s')
#                                      % (bnk_statements.name,
#                                         bnk_statements.balance_end_real))

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            journal_id = vals.get('journal_id',
                                  self._context.get('default_journal_id',
                                                    False))
            journal = self.env['account.journal'].browse(journal_id)
            if journal.type == 'bank':
                sequence = self.env.ref(
                    'pti_bank_statement.sequence_bank_statement')
                val = sequence.with_context(
                    ir_sequence_date=vals.get('date')).next_by_id()
            elif journal.type == 'cash':
                sequence = self.env.ref(
                    'pti_bank_statement.sequence_bank_statement_cash')
                val = sequence.with_context(
                    ir_sequence_date=vals.get('date')).next_by_id()
            else:
                val = journal.sequence_id.with_context(
                    ir_sequence_date=vals.get('date')).next_by_id()
            vals['name'] = val
        return super(AccountBankStatement, self).create(vals)

    @api.multi
    def write(self, vals):
        bnk_stmt_update = super(AccountBankStatement, self).write(vals)
        if bnk_stmt_update:
            for statement in self:
                statement._set_next_balance(statement.journal_id.id, statement.id, statement.balance_end)
                statement._update_balance_end_real(statement.balance_end)

        return bnk_stmt_update
    
    @api.model
    def _update_balance_end_real(self, balance_end):
        if self.balance_end_real != balance_end:
            self.balance_end_real = balance_end
        
    @api.model
    def _set_next_balance(self, journal_id, bnk_stmt_id, balance):
        next_bnk_stmt = self.search([('journal_id', '=', journal_id),
                                     ('id', '>', bnk_stmt_id)],
                                    order="id asc")
        balance_start = self.balance_end
        diff = self.balance_end - balance
        if next_bnk_stmt:
            for bnk_stmt in next_bnk_stmt:
                bnk_stmt.write(
                    {'balance_start': balance_start})
                if bnk_stmt.balance_end != bnk_stmt.balance_end_real:
                    bnk_stmt.write(
                        {'balance_end_real':
                         bnk_stmt.balance_end_real + diff})
                else:
                    bnk_stmt.write(
                        {'balance_end_real': bnk_stmt.balance_end})
                balance_start = bnk_stmt.balance_end

    def check_balance(self):
        result = self._get_prev_bnk_stmt()
        if len(result) == 0:
            pass
        else:
            current_id = result[0]['id']
            ending_balance = self.search([('id', '=', current_id)]
                                         ).balance_end
            if self.balance_start != ending_balance:
                return False
        return True

    def _get_prev_bnk_stmt(self):
        cr = self._cr
        result = cr.execute('SELECT id FROM account_bank_statement WHERE '\
                            'id < %s and journal_id = %s ORDER BY id'\
                            ' DESC LIMIT 1', [(self.id),
                                              (self.journal_id.id)])
        result = self.env.cr.dictfetchall()
        return result

    @api.multi
    def button_confirm_bank(self):
        result = self._get_prev_bnk_stmt()
        if len(result) == 0:
            return super(AccountBankStatement,
                         self).button_confirm_bank()
        else:
            current_id = result[0]['id']
            state = self.search([('id', '=', current_id)]
                                ).state
            if state == 'open':
                raise ValidationError('You cannot close this Bank Statement'\
                                      ' before the last Bank Statement'\
                                      ' closed')
            else:
                return super(AccountBankStatement,
                             self).button_confirm_bank()

    @api.multi
    def open_internal_transfer(self, statement):
        context = self._context
        if not context:
            context = {}

        context.update({
            'active_model': self._name,
            'active_ids': statement,
            'active_id': len(statement) or False
        })

        created_id = self.env['account.internal.transfer'].create(
            {'statement_id': self.id,
             'journal_id': self.journal_id.id,
             'amount': 0,
             'communication': '-',
             'payment_date': self.start_date})

        view_id = self.env.ref(
            'pti_bank_statement.view_account_payment_wizard_form')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.internal.transfer',
            'view_id': view_id.id,
            'res_id': created_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            }

    @api.multi
    def open_prev_bank_statement(self):
        view_id = self.env.ref(
            'pti_bank_statement.view_bank_statement_form')
        cr = self._cr
        result = cr.execute('SELECT id FROM account_bank_statement WHERE '\
                            'id < %s and journal_id = %s ORDER BY id'\
                            ' DESC LIMIT 1', [(self.id),
                                              (self.journal_id.id)])
        result = self.env.cr.dictfetchall()
        if len(result) == 0:
            bank_statement_id = self.id
        else:
            current_id = result[0]['id']
            bank_statement_id = self.search([('id', '=', current_id)]
                                            ).id
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.bank.statement',
                'view_id': view_id.id,
                'res_id': bank_statement_id,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'current',
            }
    access_group = fields.Boolean(compute='_groups_access', string='Access groups', default=False)

class AccountBankStatementLine(models.Model):
    _inherit = ['account.bank.statement.line']
    _order = "date , statement_id,sequence, id"
    balance = fields.Float('Balance', compute="_compute_balance")
    
    
    debit = fields.Float(string='Debit', digits=0)
    credit = fields.Float(string='Credit', digits=0)

    @api.onchange('debit')
    def _onchange_debit(self):
        self.update({
            'debit' : abs(self.debit),
            'credit' : 0,
            'amount' : abs(self.debit)
        })

    @api.onchange('credit')
    def _onchange_credit(self):
        self.update({
            'debit': 0,
            'credit': abs(self.credit),
            'amount': -1 * abs(self.credit)
        })
        
#     @api.onchange('journal_id')
#     def _onchange_journal_id(self):
#         cr = self._cr
#         result = cr.execute('SELECT max(date) '\
#                             'FROM account_bank_statement '\
#                             'WHERE journal_id = %s',
#                             [(self.journal_id.id)])
#         result = self.env.cr.dictfetchall()
#         date = result[0]['max']
#         if not date:
#             self.start_date = datetime.datetime.now()
#         else:
#             self.start_date = date

    @api.onchange('date')
    def _onchange_date(self):
        if not self.statement_id.start_date <= self.statement_id.date:
            raise ValidationError('Ending Date must be equal or greater\
                than Starting Date')

    @api.multi
    def _compute_balance(self):
        i = balance = 0
        statement_id = False
        for line in self:
            statement_id = line.statement_id
            break
        statement_lines = self.env['account.bank.statement.line'].search([('statement_id','=',statement_id.id)])
        for line in statement_lines:
            if i == 0:
                start_balance = line.statement_id.balance_start
                line.balance = start_balance + line.amount
                balance = line.balance
                i = i + 1
            else:
                line.balance = balance + line.amount
                balance = line.balance

    @api.constrains('date')
    def _check_date_line_ids(self):
        if not self.date >= self.statement_id.start_date and self.date <= self.statement_id.date:
            raise ValidationError('Transactions Date must be between\
                Starting Date and Ending Date in bank statement %s' % (self.statement_id.name))

