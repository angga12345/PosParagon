from openerp import api, fields, models, _
from openerp.exceptions import UserError


class JournalSetting(models.Model):
    _name = "sale.journal.setting"
    
    name = fields.Many2one('account.journal', string="Journal")
    prefix = fields.Char(string="Prefix")
    suffix = fields.Char(string="Suffix")
    padding = fields.Integer(string="Sequence Size")
    number_increment = fields.Integer(string="Step")
    
    @api.multi
    def action_update_sequence(self):
        seq = self.name
        seq_id = seq.sequence_id.id
        sequence = self.env['ir.sequence'].search([('id','=', seq_id)])
        for set in sequence :
            set.write({'prefix': self.prefix,
                          'suffix': self.suffix,
                          'padding': self.padding,
                          'number_increment': self.number_increment})
            
class StockPicking(models.Model):
    _inherit = "stock.picking"
     
    @api.model
    def create(self, vals):
        if vals.get('partner_id'):
            partner_ids = self.env['res.partner'].search([('id','=',vals.get('partner_id'))])
            seq_id = self.env['ir.sequence'].search([('name','=','Parama Sequence out')])
            if partner_ids:
                if partner_ids[0].journal_id.name == 'Sales Parama':
                    loc_ids = self.env['stock.location'].search([('id','=',vals.get('location_dest_id'))])
                    pick_type = self.env['stock.picking.type'].search([('id','=', vals.get('picking_type_id'))])
                    sequence = pick_type.sequence_id
                    val = sequence.with_context(ir_sequence_date=self.date).next_by_id()
                    if val:
                        x = val
                        if not self.name:
                            vals['name'] = 'PRM/'+ x
        order = super(StockPicking, self).create(vals)
        return order

class Customer(models.Model):
    _inherit = "res.partner"
    
    journal_id = fields.Many2one('account.journal', string="Sales Journal", required= True)
            

class SaleJournal(models.Model):
    _inherit = "sale.order"
      
    @api.model
    def create(self, vals):
        if vals.get('partner_id'):
            partner_ids = self.env['res.partner'].search([('id','=',vals.get('partner_id'))])
            if partner_ids:
                if partner_ids[0].journal_id.name == 'Sales Parama':
                    if vals.get('name', 'New') == 'New':
                        vals['name'] = self.env['ir.sequence'].next_by_code('prm.sale.orders') or 'New'
        res = super(SaleJournal, self).create(vals)
        return res
    
    @api.multi
    def _prepare_invoice(self):
        res =super(SaleJournal, self)._prepare_invoice()
        cust = self.env['res.partner'].search([('id','=', self.partner_id.id)])
        if cust.journal_id:
            print '================================='
            res.update({'journal_id' : cust.journal_id.id})
        return res
    
class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    @api.multi
    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res =super(AccountInvoice, self)._onchange_partner_id()
        cust = self.env['res.partner'].search([('id','=', self.partner_id.id)])
        if self.partner_id :
            if cust.journal_id:
                self.journal_id = cust.journal_id.id
        return res
    
    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            val = False
            if invoice.journal_id.name == 'Sales Parama':
                type_code_inv = invoice.type_code_invoice or ''
                type = invoice.type or ''
                if type_code_inv =='':
                    raise UserError(_("Please choose the type code of this invoice"))
                elif type_code_inv == '10':
                    if type == 'out_invoice':
                        sequence = self.env.ref('sale_journal_partner.sequence_parama_invoice_number')
                        val = sequence.with_context(ir_sequence_date=self.date).next_by_id()
                    elif type == 'out_refund':
                        sequence = self.env.ref('sale_journal_partner.sequence_parama_cancel_invoice_number')
                        val = sequence.with_context(ir_sequence_date=self.date).next_by_id()
                        type_code_inv = '11'
                    if val:
                        x = val
                        a = x[-8:]
                        if invoice.number:
                            invoice.number = 'PRM/' + a[:2] + type_code_inv + a[2:]
                            invoice.move_id.name = 'PRM/' + a[:2] + type_code_inv + a[2:]
                     
                elif type_code_inv == '20':
                    if type == 'out_invoice':
                        sequence = self.env.ref('sale_journal_partner.sequence_parama_invoice_number')
                        val = sequence.with_context(ir_sequence_date=self.date).next_by_id()
                    elif type == 'out_refund':
                        sequence = self.env.ref('sale_journal_partner.sequence_parama_cancel_invoice_number')
                        val = sequence.with_context(ir_sequence_date=self.date).next_by_id()
                        type_code_inv = '21'
                    if val:
                        x = val
                        a = x[-8:]
                        if invoice.number:
                            invoice.number = 'PRM/' + a[:2] + type_code_inv + a[2:]
                            invoice.move_id.name = 'PRM/' + a[:2] + type_code_inv + a[2:]
            
                elif type_code_inv == '30':
                    if type == 'in_refund':
                        sequence = self.env.ref('sale_journal_partner.sequence_parama_debit_number')
                        val = sequence.with_context(ir_sequence_date=self.date).next_by_id()
                    elif type == 'in_invoice':
                        sequence = self.env.ref('sale_journal_partner.sequence_parama_cancel_debit_number')
                        val = sequence.with_context(ir_sequence_date=self.date).next_by_id()
                    if val:
                        x = val
                        a = x[-8:]
                        if invoice.number:
                            invoice.number = 'PRM/' + a[:2] + type_code_inv + a[2:]
                            invoice.move_id.name = 'PRM/' + a[:2] + type_code_inv + a[2:]
                      
                elif type_code_inv == '40':
                    if type == 'out_refund':
                        sequence = self.env.ref('sale_journal_partner.sequence_parama_credit_number')
                        val = sequence.with_context(ir_sequence_date=self.date).next_by_id()
                    elif type == 'out_invoice':
                        sequence = self.env.ref('sale_journal_partner.sequence_parama_cancel_credit_number')
                        val = sequence.with_context(ir_sequence_date=self.date).next_by_id()
                        type_code_inv = '44'
                    if val:
                        x = val
                        a = x[-8:]
                        if invoice.number:
                            invoice.number = 'PRM/' + a[:2] + type_code_inv + a[2:]
                            invoice.move_id.name = 'PRM/' + a[:2] + type_code_inv + a[2:]
                        
                res = self.write({'state': 'open', 'date_posted' : self.date})
        return res
