from openerp import models, fields, api, _

class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"
    
    product_global = fields.Many2many('product.product', 'product_product_rel', 'pricelist_item_id', string="Product Global")
    
    @api.onchange('applied_on')
    def _onchange_apply_on(self):
        #fill produk_pwp_ids Automatically after fill Price rule 
        cr = self.pool.cursor()
        self.env
        #print 'TEST',self.pool.get('product.template').search(cr, self.env.uid, [])
        if self.applied_on == '3_global':
            self.product_global = self.pool.get('product.product').search(cr, self.env.uid, [])
        else:
            self.product_global = False