from openerp import models, api, _


class res_partner(models.Model):
    _inherit = "res.partner"
            
    @api.model
    def create(self, values):
        if values.get('is_shop') == True:
            values['store_code'] = self.env['ir.sequence'].next_by_code('store.code.seq')
        return super(res_partner, self).create(values)
    
            