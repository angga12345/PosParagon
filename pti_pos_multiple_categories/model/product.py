from openerp import api, fields, models, _


class product_template(models.Model):
    _inherit = 'product.template'

    category_ids = fields.Many2many('product.category', string="Category")
    pos_category_ids = fields.Many2many('pos.product.category', string="POS Categories")


class product_pricelist_item(models.Model):
    _inherit = 'product.pricelist.item'

    category_ids = fields.Many2many('pos.product.category', string="Category")

    @api.multi
    @api.depends('category_ids', 'product_tmpl_id', 'product_id', 'compute_price', 'fixed_price', \
        'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge')
    def _get_pricelist_item_name_price(self):
        for item in self:
            if item.category_ids:
                ctg = ''
                for category in item.category_ids:
                    ctg = ctg + str(category.name) + ' ' 
                item.name = _("Category: %s") % (ctg)
            elif item.product_tmpl_id:
                item.name = item.product_tmpl_id.name
            elif item.product_id:
                item.name = item.product_id.display_name.replace('[%s]' % item.product_id.code, '')
            else:
                item.name = _("All Products")          
            if item.compute_price == 'fixed':
                item.price = ("%s %s") % (item.fixed_price, item.pricelist_id.currency_id.name)
            elif item.compute_price == 'percentage':
                item.price = _("%s %% discount") % (item.percent_price)
            else:
                item.price = _("%s %% discount and %s surcharge") % (abs(item.price_discount), item.price_surcharge)


class PosProductCategories(models.Model):
    _name = 'pos.product.category'
    _description = 'Product Category for POS'

    name = fields.Char(string="Name")
    parent_id = fields.Many2one('pos.product.category', string="Parent")
