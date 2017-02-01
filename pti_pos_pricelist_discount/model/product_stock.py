from openerp import http, models, fields, api

class product_stock(models.Model):
    _inherit = 'product.product'
    
    qty_per_loc = fields.Float('Qty perlocation')

    @api.model
    def stock_location_on_hand(self, prod_id, loc_id):
        stock_obj = self.env['stock.quant'].search([('product_id','=',prod_id),('location_id','=',loc_id)])
       
        on_hand = 0 
        if stock_obj:
            for stock in stock_obj :
                on_hand = on_hand + stock.qty
        #update Qty per location
        self.env.cr.execute('update product_product '
                               'set qty_per_loc=%s where id=%s', (on_hand, prod_id))     
        
        
        return on_hand