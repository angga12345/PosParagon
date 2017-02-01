from openerp import models, fields,api, _

class AccountInvoice(models.Model):
    _inherit='account.invoice'

    @api.multi
    def confirm_paid(self):
        res = super(AccountInvoice,self).confirm_paid()
        if self.state=='paid' and self.origin:
            sale_val=self.env['sale.order'].search([('name','=',self.origin)])
            val=self.env['sale.order'].browse([sale_val.id])
            val.write({'state':'done'})
        return res

class accountmoveline(models.Model):
    _inherit='account.move.line'
     
    @api.multi
    def remove_move_reconcile(self):
        sale_val=self.env['account.invoice'].search([('id','=',self.collector_invoice_id.id)])
        val=self.env['sale.order'].search([('name','=',sale_val.origin)])
        for so in val:
            so.write({'state':'sale'})
        return super(accountmoveline,self).remove_move_reconcile()
