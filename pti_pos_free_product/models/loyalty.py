from openerp import fields, models


class LoyaltyRule(models.Model):
    _inherit = 'loyalty.rule'

    applied = fields.Selection([('all', 'All Product'),
                                ('one', 'One of Products')],
                               string="Apply On", default='one')
    type = fields.Selection([('all', 'All'),
                             ('product', 'Product'),
                             ('category', 'Category')], string="Type")
