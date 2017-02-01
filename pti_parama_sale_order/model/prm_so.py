from openerp import fields, models, api, _

class account_prm_so(models.Model):
    _inherit = "account.invoice"
    
    parama_so_id = fields.Char("Parama SO ID")
    
class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.multi
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for so in self:
            invoice_ids = self.env['account.invoice'].search([('parama_so_id','=',so.id)])
            for inv in invoice_ids:
                inv.write({'parama_so_id':False})
        return res
    
    
    