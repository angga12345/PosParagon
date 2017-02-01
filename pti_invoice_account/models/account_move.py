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
from openerp.exceptions import  Warning
from openerp.exceptions import except_orm, Warning, RedirectWarning

class AccountMove(models.Model):
    _inherit = "account.move"
    
    dc_id = fields.Many2one('res.partner', "Distribution Center", default=lambda self: self.journal_id.dc_id)
    year = fields.Integer('Year')
    month = fields.Selection([(1, 'January'), (2, 'February'),(3, 'March'),
                              (4, 'April'), (5, 'Mei'),(6, 'Juni'),
                              (7, 'July'), (8, 'Agustus'),(9, 'September'),
                              (10, 'October'), (11, 'November'),(12, 'December'),], 'Month')
    @api.model
    def create(self, values):
        if values.get('date'):
            date = values['date'].split('-')
            values['year'] = int(date[0])
            values['month'] = int(date[1].strip("0") if date[1] !='10' else date[1])
        if not values.get('dc_id'):
            if values.get('journal_id'):
                journal_id = self.env['account.journal'].browse([values.get('journal_id')])
                values['dc_id'] = journal_id.dc_id.id
        if not values.get('dc_id'):
            partner = False
            if values.get('partner_id'):
                partner = self.env['res.partner'].browse([values['partner_id']])
            values['dc_id'] = self.env.user.partner_id.dc_id.id or partner
        if not values.get('dc_id'):
            if values.get('line_ids'):
                if len(values['line_ids'][0])==3:
                    invoice_line_dict = values['line_ids'][0][2]
                    if invoice_line_dict.get('invoice_id'):
                        inv = self.env['account.invoice'].browse([invoice_line_dict.get('invoice_id')])
                        values['dc_id'] = inv.dc_id.id

        res = super(AccountMove, self).create(values)
        return res
    
    @api.multi
    def post(self):
        res = super(AccountMove,self).post()
        for move in self:
            for line in move.line_ids:
                warning_type = self.env['account.account.type'].search([('id','=',line.account_id.user_type_id.id)])
                type_account = warning_type.type
                if ((type_account == 'receivable' or type_account == 'payable') and line.partner_id.id == False) and (move.journal_id.type != 'general'):
                    raise Warning("Fill partner for payable or receivable account.")
        return res

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    _order = "date asc, id asc"
    
    dc_id = fields.Many2one('res.partner', "Distribution Center", default=lambda self: self.journal_id.dc_id)
    year = fields.Integer('Year')
    month = fields.Selection([(1, 'January'), (2, 'February'),(3, 'March'),
                              (4, 'April'), (5, 'Mei'),(6, 'Juni'),
                              (7, 'July'), (8, 'Agustus'),(9, 'September'),
                              (10, 'October'), (11, 'November'),(12, 'December'),], 'Month')
    debit = fields.Monetary(default=0.0, currency_field=False)
    credit = fields.Monetary(default=0.0, currency_field=False)
    symbol = fields.Char('Symbol', related="move_id.currency_id.symbol")
    
    @api.model
    def create(self, values):
        date = False
        if not values.get('dc_id'):
            if values.get('journal_id'):
                journal_id = self.env['account.journal'].browse([values.get('journal_id')])
                values['dc_id'] = journal_id.dc_id.id
        if not values.get('dc_id'):
            if values.get('name'):
                invoice_id = self.env['account.invoice'].search([('number','=',values.get('name'))])
                values['dc_id'] = invoice_id.dc_id.id
        if not values.get('dc_id'):
            if values.get('invoice_id'):
                invoice = self.env['account.invoice'].browse([values['invoice_id']])
                date = invoice.date_invoice
                values['dc_id'] = invoice.partner_id.dc_id.id or self.env.user.partner_id.dc_id.id or invoice.dc_id.id
        if values.get('date_maturity'):
            date = values['date_maturity'].split('-')
            values['year'] = int(date[0])
            values['month'] = int(date[1].strip("0") if date[1] !='10' else date[1])

        res = super(AccountMoveLine, self).create(values)
        return res
