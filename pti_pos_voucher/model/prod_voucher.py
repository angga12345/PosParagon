from openerp import models, fields, api

class product_voucher(models.Model):
    _inherit = 'product.product'

    @api.model
    def deactive_voucher(self, prod_id):
        prod_obj = self.env['product.product'].search([('id','=',prod_id)],limit=1)
        values = {}
          
        if prod_obj:
            values['active'] =  False
            
            prod_obj[0].write(values)
            print "-------------------------SET DEACTIVE----------------------------------------"
             
        
        
        return True
