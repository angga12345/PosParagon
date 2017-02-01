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

class AccountInternalTransfer(models.TransientModel):
    _name = 'account.internal.transfer'

    statement_id = fields.Many2one('account.bank.statement',
                                   'Bank Statement')
    payment_type = fields.Selection([('outbound', 'Send Money'),
                                     ('inbound', 'Receive Money'),
                                     ('transfer', 'Internal Transfer')],
                                    string='Payment Type',
                                    required=True,
                                    default='transfer')
    journal_id = fields.Many2one('account.journal',
                                 string='Payment Method',
                                 required=True,
                                 domain=[('type', 'in',
                                          ('bank', 'cash'))])
    destination_journal_id = fields.Many2one('account.journal',
                                             string='Transfer To',
                                             domain=[('type', 'in',
                                                      ('bank',
                                                       'cash'))])
    amount = fields.Float(string='Payment Amount', required=True)
    payment_date = fields.Date(string='Payment Date',
                                default=fields.Date.context_today,
                               required=True, copy=False)
    communication = fields.Char(string='Memo', required=True)
    payment_method_id = fields.Many2one('account.payment.method',
                                        string='Payment Type',
                                        domain=[('payment_type', '=',
                                                 'outbound')],
                                        oldname="payment_method")
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self:
                                  self.env.user.company_id.currency_id)

    @api.constrains('payment_date')
    def _check_payment_date(self):
        payment_date = self.payment_date
        start_date = self.statement_id.start_date
        ending_date = self.statement_id.date

        if payment_date < start_date or payment_date > ending_date:
            raise ValidationError('Payment Date must be between\
                                    Starting date and Ending Date')

    @api.multi
    def bank_statement_action(self):
        statement_id = self._context['active_id']
        bank_statement_obj = self.env['account.bank.statement']
        bank_line = self.env['account.bank.statement.line']
        # GET TRANSFER ACCOUNT FROM ACCOUNTING SETTING. SO WOULD DYNAMIC
        coa = self.env['res.company'].search([], limit=1)
        if not coa.transfer_account_id.id:
            raise UserError(_("Account for transfer not exist"))
        if not coa.transfer_account_id.reconcile:
            msg = "Account can't reconcile. Please Check account %s" % (coa.transfer_account_id.name,)
            raise UserError(_(msg))
        data = {'credit': 0, 'debit': 0, 'account_id': coa.transfer_account_id.id, 'name': 'internal transfer'}
        bank_statement_dest = bank_statement_obj.search(
            [('journal_id', '=', self.destination_journal_id.id),('state','=','open')], limit=1)

        if not bank_statement_dest:
            raise ValidationError('There are no Open Bank Statement in\
             this Date')
        else:
            for line in bank_statement_dest:
                if (self.payment_date >= line.start_date and
                        self.payment_date <= line.date):
                    if line.state == 'confirm':
                        raise ValidationError('There are no Open Bank Statement in\
                         this Date')
                    else:
                        current = bank_line.create({'date': self.payment_date,
                                           'name': self.communication,
                                           'amount': self.amount * -1,
                                           'statement_id' : statement_id})
                        data['debit'] = self.amount
                        data['credit'] = 0
                        move = current.process_reconciliation(None, None, [data])
                        destination = bank_line.create({'date': self.payment_date,
                                          'name': self.communication,
                                          'amount': self.amount,
                                          'statement_id' : bank_statement_dest.id})
                        data['debit'] = 0
                        data['credit'] = self.amount
                        move2 = destination.process_reconciliation(None, None, [data])
                        # search account move line which have same account then reconcile directly
                        aml = self.env['account.move.line'].search([('move_id','in',(move.id,move2.id)),
                                                              ('account_id','=',coa.transfer_account_id.id)])
                        aml.auto_reconcile_lines()
                else:
                    raise ValidationError('Can not do internal transfer because in %s transaction open between %s and %s'% (bank_statement_dest.name,str(line.start_date),str(line.date)))

