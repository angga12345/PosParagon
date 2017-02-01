from openerp import api, fields, models, _
from datetime import datetime,timedelta

class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    @api.multi
    def generate_CN(self):
        res = False
        if self.picking_type_id.is_retur:
            add_days = self.partner_id.property_payment_term_id.line_ids
            for day in add_days:
                if day.value == 'balance':
                    day = day.days
            add_date = datetime.now().date() + timedelta(days=day)            
#  make in object account.invoice
            obj= {
                            'type' : 'out_refund',
                            'type_code_invoice':'40',
                            'state' : 'draft',
                            'partner_id' : self.partner_id.id,
                            'payment_term_id' :self.partner_id.property_payment_term_id.id,
                            'currency_id' : self.company_id.currency_id.id,
                            'journal_id' : '76',
                            'account_id' : self.partner_id.property_account_receivable_id.id,
                            'dc_id' : self.partner_id.dc_id.id,
                            'origin': self.name,
                            'date_invoice' : datetime.now().date(),
                            'user_id' : self.sale_id.user_id.id,                        # if not have SO ?
                            'fiscal_position_id':self.sale_id.fiscal_position_id.id,    # if not have SO ?
                            'date_due':add_date,
                      }
            total = 0
            print 'sini'
            obj_invoice = self.env['account.invoice'].create(obj)
            print 'sampai sini'
#  make in object account.invoice.line
        
            for order in self.pack_operation_product_ids:
                if self.sale_id.id == False:
                    invoice_line = {
                                              'invoice_id':obj_invoice.id,
                                              'product_id':order.product_id.id,
                                              'name': order.product_id.name,
                                              'account_id':order.product_id.categ_id.property_account_income_categ_id.id,
                                              'quantity':order.qty_done,
                                              'uom_id':order.product_id.uom_id.id,
                                              'price_unit':order.product_id.lst_price,
                                              'invoice_line_tax_ids':[(6,0,order.product_id.taxes_id.ids)], 
                                              }
                    one_invoice = self.env['account.invoice.line'].create(invoice_line)
                    
                    taxes = self.env['account.tax'].search([('id','in',order.product_id.taxes_id.ids)])
                    for tax in taxes:
                        for liness in one_invoice:
                            tax_ = liness.price_subtotal * tax.amount/100
                            total = tax_ + total
                            
#  make in object account.invoice.tax
                    tax_line = {
                                'invoice_id':obj_invoice.id,
                                'name':tax.name,
                                'account_id':tax.account_id.id,
                                'amount':total,          
                                }
                    
                else:
                    product_id = False
                    for line in self.sale_id.order_line:
                        if order.product_id.id == line.product_id.id and line.product_id.id != product_id :
                            invoice_line = {
                                          'invoice_id':obj_invoice.id,
                                          'product_id':order.product_id.id,
                                          'name': order.product_id.name,
                                          'account_id':order.product_id.categ_id.property_account_income_categ_id.id,
                                          'quantity':order.qty_done,
                                          'uom_id':order.product_id.uom_id.id,
                                          'price_unit':order.product_id.lst_price,
                                          'discount_m2m':[(6,0,line.discount_m2m.ids)],
                                          'invoice_line_tax_ids':[(6,0,order.product_id.taxes_id.ids)], 
                                          }
                            one_invoice = self.env['account.invoice.line'].create(invoice_line)
                            product_id = one_invoice.product_id.id
                            taxes = self.env['account.tax'].search([('id','in',line.tax_id.ids)])
                            for tax in taxes:
                                for liness in one_invoice:
                                    tax_ = liness.price_subtotal * tax.amount/100
                                    total = tax_ + total
                                    
#  make in object account.invoice.tax
                            tax_line = {
                                        'invoice_id':obj_invoice.id,
                                        'name':tax.name,
                                        'account_id':tax.account_id.id,
                                        'amount':total,          
                                        }
            self.env['account.invoice.tax'].create(tax_line)
        return res