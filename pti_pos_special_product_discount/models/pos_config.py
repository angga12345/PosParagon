from openerp import models, fields, api, _

class PosConfig(models.Model):
    _inherit = "pos.config"
    
    show_discount = fields.Boolean(string="Show Discount Text", default=False)
#     discount_text = fields.Char(string= "Discount Text")
 