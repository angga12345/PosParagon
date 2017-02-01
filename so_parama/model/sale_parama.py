from openerp import api, fields, models, _
from openerp.exceptions import except_orm


class SaleParama(models.Model):
    _inherit = "sale.order"
    
    @api.multi
    def write(self, vals):
        res = super(SaleParama, self).write(vals)
        if self.name :
            if vals.get('partner_id'):
                partner_ids = self.env['res.partner'].search([('id','=',vals.get('partner_id'))])
                if partner_ids :
                    if partner_ids[0].journal_id.name == 'Sales Paragon' and 'PRM/' in self.name :
                        raise except_orm(_('Warning!'),_('Customer does not correspond SO company'))
                    elif partner_ids[0].journal_id.name == 'Sales Parama' and 'PRM/' not in self.name :
                        raise except_orm(_('Warning!'),_('Customer does not correspond SO company'))
        return res
    
    @api.multi
    def quick_action_confirm(self):
        res = super(SaleParama, self).quick_action_confirm()
        for so in self :
            if so.partner_id.name == 'Parama':
                if so.partner_id.journal_id.name != 'Sales Parama':
                    raise except_orm(_('Warning!'),_("Customer is Parama, But sales journal in Customer is not Sales Parama !!"))
                elif so.warehouse_id.name != 'Paragon:Parama':
                    raise except_orm(_('Warning!'),_("Customer is Parama, please change Warehouse to 'Paragon:Parama' !!"))
        return res
    
    
class stock_validate_transfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'
    
    @api.multi
    def process(self):
        res = super(stock_validate_transfer, self).process()
        for pack in self.pick_id :
            if pack.partner_id.name == 'Parama' and pack.partner_id.journal_id.name == 'Sales Parama' and not pack.state_shipment :
                pack.write({'state_shipment': "done"})
        return res
            