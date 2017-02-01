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
from datetime import datetime, date
import time

# mapping invoice type to refund type
TYPE2REFUND = {
    'out_invoice': 'out_refund',        # Customer Invoice
    'in_invoice': 'in_refund',          # Vendor Bill
    'out_refund': 'out_invoice',        # Customer Refund
    'in_refund': 'in_invoice',          # Vendor Refund
}
MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')
class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    collector_id = fields.Many2one('res.partner', "Collector")
    type_code_invoice = fields.Selection([
        ('10', 'Normal Sales'), 
        ('20', 'Consignment Sales'),
        ('30', 'Debit Note'),
        ('40', 'Credit Note')], 'Type Code Invoice', required=True, default='10')
    date_posted = fields.Date(string="Date posted", required=False, readonly=True, copy=False)

    _SELECT_STATE = [
            ('draft','Draft'),
            ('proforma', 'Pro-forma'),
            ('proforma2', 'Pro-forma'),
            ('open', 'Open'),
            ('paid', 'Paid'),
            ('cancel', 'Cancelled'),
            ('refund', 'Cancelled/Refund'),
            ('done', 'Done')]

    refund_cancel = fields.Boolean(default=False)

    state_refund = fields.Selection([
            ('draft','Draft'),
            ('proforma', 'Pro-forma'),
            ('proforma2', 'Pro-forma'),
            ('open', 'Open'),
            ('paid', 'Paid'),
            ('cancel', 'Cancelled'),
            ('refund', 'Cancelled/Refund'),
            ('done', 'Done'),
        ], string='Status', index=True, readonly=True,
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Pro-forma' status is used the invoice does not have an invoice number.\n"
             " * The 'Open' status is used when user create invoice, an invoice number is generated. Its in open status till user does not pay invoice.\n"
             " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice.")

    retur_faktur = fields.Boolean('Nota Retur Faktur pajak provided', default=True)

    @api.onchange('retur_faktur')     
    def _onchange_retur_faktur(self):         
        retur = self.retur_faktur         
        if retur == True:             
            for il in self.invoice_line_ids :                 
                il.invoice_line_tax_ids = il.product_id.taxes_id         
        elif retur == False:             
            ppns = []             
            fiscal_position = self.env['account.fiscal.position'].search([('name', '=', 'EXPENSE_TAX')],limit=1)             
            if fiscal_position.id is False:
                raise UserError(_("Your Fiscal Position EXPENSE_TAX is not Active , Please Activate or Create fiscal position EXPENSE_TAX First"))
            else:
                for test_jum in  fiscal_position.tax_ids.search([('tax_src_id.name','=',self.invoice_line_ids.product_id.taxes_id.name)]):                 
                    self.invoice_line_ids.invoice_line_tax_ids = test_jum.tax_dest_id


    @api.multi
    def print_inv(self):
        return self.env['report'].get_action(self, 'pti_invoice_report.report_inv')

    @api.onchange('date_invoice')
    def _onchange_date_invoice(self):
        res = False
        if self.date_invoice:
            date_invoice = self.date_invoice
            fmt = '%Y-%m-%d'
            date_inv = datetime.strptime(date_invoice, fmt)

            current_date = datetime.strptime(str(datetime.now().date()), fmt)
            daysDiff = (current_date-date_inv).days
            if daysDiff > 60:
                res = {}
                res['warning'] = {
                    'title': "Warning",
                    'message': 'Failed : Date Changes is more than 2 months'
                    }
                self.date_invoice = current_date
                return res
        return res
    
    @api.model
    def create(self,vals):
        """This function super using for Fill invoice date"""
        if vals.get('date_invoice') is False:
            vals['date_invoice']=fields.Datetime.now()
        res=super(AccountInvoice,self).create(vals)
        return res

    @api.one
    @api.depends('state','state_refund')
    def DefaultState(self):
       res = False
       if self.state_refund == 'refund' or self.state_refund == 'done':
          res = self.state_refund
       else:
          res = self.state
       self.state_merge = res

    state_merge = fields.Selection(compute='DefaultState', string='State', selection=_SELECT_STATE)

    @api.multi
    def invoice_validate(self):
        date = datetime.strptime(fields.Datetime.now(), "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d')
        for invoice in self:
            if invoice.journal_id.other_journal:
                continue
            val = False
            #refuse to validate a vendor bill/refund if there already exists one with the same reference for the same partner,
            #because it's probably a double encoding of the same bill/refund
            if invoice.type in ('in_invoice', 'in_refund') and invoice.reference:
                if self.search([('type', '=', invoice.type), ('reference', '=', invoice.reference), ('company_id', '=', invoice.company_id.id), ('commercial_partner_id', '=', invoice.commercial_partner_id.id), ('id', '!=', invoice.id)]):
                    raise UserError(_("Duplicated vendor reference detected. You probably encoded twice the same vendor bill/refund."))

            #Create sequence invoice by type code invoice
            type_code_inv = invoice.type_code_invoice or ''
            type = invoice.type or ''
            if type_code_inv =='':
                raise UserError(_("Please choose the type code of this invoice"))
            elif type_code_inv == '10':
                if type == 'out_invoice':
                    sequence = self.env.ref('pti_invoice_account.sequence_invoice_number')
                    val = sequence.with_context(ir_sequence_date=date).next_by_id()
                elif type == 'out_refund':
                    sequence = self.env.ref('pti_invoice_account.sequence_cancel_invoice_number')
                    val = sequence.with_context(ir_sequence_date=date).next_by_id()
                    type_code_inv = '11'
                if val:
                    x = val
                    a = x[-8:]
                    if invoice.number:
                        invoice.number = a[:2] + type_code_inv + a[2:]
                        invoice.move_id.name = a[:2] + type_code_inv + a[2:]

            elif type_code_inv == '20':
                if type == 'out_invoice':
                    sequence = self.env.ref('pti_invoice_account.sequence_invoice_number')
                    val = sequence.with_context(ir_sequence_date=date).next_by_id()
                elif type == 'out_refund':
                    sequence = self.env.ref('pti_invoice_account.sequence_cancel_invoice_number')
                    val = sequence.with_context(ir_sequence_date=date).next_by_id()
                    type_code_inv = '21'
                if val:
                    x = val
                    a = x[-8:]
                    if invoice.number:
                        invoice.number = a[:2] + type_code_inv + a[2:]
                        invoice.move_id.name = a[:2] + type_code_inv + a[2:]

            elif type_code_inv == '30':
                if type == 'in_refund':
                    sequence = self.env.ref('pti_invoice_account.sequence_debit_sales')
                    val = sequence.with_context(ir_sequence_date=date).next_by_id()
                elif type == 'in_invoice':
                    sequence = self.env.ref('pti_invoice_account.sequence_cancel_debit_sales')
                    val = sequence.with_context(ir_sequence_date=date).next_by_id()
                if val:
                    x = val
                    a = x[-8:]
                    if invoice.number:
                        invoice.number = a[:2] + type_code_inv + a[2:]
                        invoice.move_id.name = a[:2] + type_code_inv + a[2:]

            elif type_code_inv == '40':
                if type == 'out_refund':
                    sequence = self.env.ref('pti_invoice_account.sequence_credit_sales')
                    val = sequence.with_context(ir_sequence_date=date).next_by_id()
                if type == 'out_invoice':
                    sequence = self.env.ref('pti_invoice_account.sequence_cancel_credit_sales')
                    val = sequence.with_context(ir_sequence_date=date).next_by_id()
                    type_code_inv = '44'
                if val:
                    x = val
                    a = x[-8:]
                    if invoice.number:
                        invoice.number = a[:2] + type_code_inv + a[2:]
                        invoice.move_id.name = a[:2] + type_code_inv + a[2:]

        return self.write({'state': 'open', 'date_posted' : fields.Datetime.now()})

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        values = super(AccountInvoice, self)._prepare_refund(invoice, date_invoice, date, description, journal_id) 
        values['type_code_invoice'] = invoice.type_code_invoice
        return values
    
    @api.onchange('partner_id','company_id', 'type')
    def _onchange_partner_id(self):
        type = ''
        if not self.partner_id.is_team_leader and not self.partner_id.is_consignment and not self.type == 'out_refund':
            type = '10'
        elif self.partner_id.is_team_leader or self.partner_id.is_consignment or not self.type == 'out_refund':
            type = '20'
        elif self.type == 'out_refund':
            type = '40'
        else:
            next
        self.type_code_invoice = type
        super(AccountInvoice, self)._onchange_partner_id()
        
    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        for line in self.invoice_line_ids:
            price_unit = line.price_unit
            for discount_product in line.discount_m2m:
                if discount_product.id:
                    price_unit = price_unit * (1 - (discount_product.percentage or 0.0) / 100.0)
                    
            taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, 
                                                          line.product_id, self.partner_id)['taxes']
            for tax in taxes:
                val = {
                    'invoice_id': self.id,
                    'name': tax['name'],
                    'tax_id': tax['id'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'account_analytic_id': tax['analytic'] and line.account_analytic_id.id or False,
                    'account_id': self.type in ('out_invoice', 'in_invoice') and (tax['account_id'] or line.account_id.id) or (tax['refund_account_id'] or line.account_id.id),
                }

                # If the taxes generate moves on the same financial account as the invoice line,
                # propagate the analytic account from the invoice line to the tax line.
                # This is necessary in situations were (part of) the taxes cannot be reclaimed,
                # to ensure the tax move is allocated to the proper analytic account.
                if not val.get('account_analytic_id') and line.account_analytic_id and val['account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id

                key = tax['id']
                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
        return tax_grouped

    @api.model
    def _refund_cleanup_lines(self, lines):
        """ Convert records to dict of values suitable for one2many line creation

            :param recordset lines: records to convert
            :return: list of command tuple for one2many line creation [(0, 0, dict of valueis), ...]
        """
        result = []
        for line in lines:
            values = {}
            for name, field in line._fields.iteritems():
                if name in MAGIC_COLUMNS:
                    continue
                elif field.type == 'many2one':
                    values[name] = line[name].id
                elif field.type not in ['many2many', 'one2many']:
                    values[name] = line[name]
                elif name == 'invoice_line_tax_ids':
                    values[name] = [(6, 0, line[name].ids)]
                elif name == 'discount_m2m':
                    values[name] = [(6, 0, line[name].ids)]
            result.append((0, 0, values))
        return result

    @api.model
    def tax_line_move_line_get(self):
        res = []
        for tax_line in self.tax_line_ids:
            res.append({
                'tax_line_id': tax_line.tax_id.id,
                'type': 'tax',
                'name': tax_line.name,
                'price_unit': tax_line.amount,
                'quantity': 1,
                'price': tax_line.amount,
                'account_id': tax_line.account_id.id,
                'account_analytic_id': tax_line.account_analytic_id.id,
                'dc_id' : tax_line.invoice_id.dc_id.id,
            })
        return res

    @api.model
    def line_get_convert(self, line, part):
        account_move_line_value = super(AccountInvoice, self).line_get_convert(line, part)
        account_move_line_value['dc_id'] = line.get('dc_id', False)
        return account_move_line_value

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    discount_m2m = fields.Many2many('discount.discount',string="Discounts")
    qty_returned = fields.Float(string='Returned', copy=False, digits=dp.get_precision('Product Unit of Measure'), default=0.0)
    is_free = fields.Boolean('Free product', default=False)
    
    @api.one
    @api.depends('price_unit', 'discount_m2m', 'invoice_line_tax_ids', 'quantity', 'qty_returned',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit
        for discount_product in self.discount_m2m:
            if discount_product.id:
                price = price * (1 - (discount_product.percentage or 0.0) / 100.0)
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, 
                                                          product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
    
    product_brand = fields.Many2one('product.brand', "Brand") # this field added for dynamic report in account.invoice.report
    price_subtotal = fields.Monetary(string='Amount',
        store=True, readonly=True, compute='_compute_price')
    price_subtotal_signed = fields.Monetary(string='Amount Signed', currency_field='company_currency_id',
        store=True, readonly=True, compute='_compute_price',
        help="Total amount in the currency of the company, negative for credit notes.")
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.env.cr.execute("select pb.id from (select product_brand_id from product_brand_product_template_rel where product_template_id="+ str(self.product_id.product_tmpl_id.id) +") as data join  product_brand pb on pb.id = data.product_brand_id and pb.name ilike 'brand:%';")
            res = self.env.cr.dictfetchall()
            if res:
                self.product_brand = res[0]['id'] or False
        return super(AccountInvoiceLine, self)._onchange_product_id()
    
class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"
    
    @api.multi
    def check_confirm_bank(self):
        context = dict(self._context or {})
        if not context.get('next', False):
            action_rec = self.env['ir.model.data'].xmlid_to_object('pti_invoice_account.action_confirm_validation')
            if action_rec:
                action = action_rec.read([])[0]
                return action
        super(AccountBankStatement, self).check_confirm_bank()


class AccountJournal(models.Model):
    _inherit = "account.journal"

    other_journal = fields.Boolean('Other Journal', default=False)
