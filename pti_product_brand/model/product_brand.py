from openerp import models, fields, api, _
from openerp.exceptions import UserError
from openerp.exceptions import except_orm
import psycopg2


class product_template(models.Model):
    _inherit = "product.template"
    
    #store = fields.Many2many('pos.config','pos_config_product_product_rel', 'product_product_id', 'pos_config_id', string='Store', copy=True)
    
    def create_variant_ids(self, cr, uid, ids, context=None):
        product_obj = self.pool.get("product.product")
        ctx = context and context.copy() or {}
        if ctx.get("create_product_variant"):
            return None

        ctx.update(active_test=False, create_product_variant=True)

        tmpl_ids = self.browse(cr, uid, ids, context=ctx)
        for tmpl_id in tmpl_ids:

            # list of values combination
            variant_alone = []
            all_variants = [[]]
            for variant_id in tmpl_id.attribute_line_ids:
                if len(variant_id.value_ids) == 1:
                    variant_alone.append(variant_id.value_ids[0])
                temp_variants = []
                for variant in all_variants:
                    for value_id in variant_id.value_ids:
                        temp_variants.append(sorted(variant + [int(value_id)]))
                if temp_variants:
                    all_variants = temp_variants

            # adding an attribute with only one value should not recreate product
            # write this attribute on every product to make sure we don't lose them
            for variant_id in variant_alone:
                product_ids = []
                for product_id in tmpl_id.product_variant_ids:
                    if variant_id.id not in map(int, product_id.attribute_value_ids):
                        product_ids.append(product_id.id)
                product_obj.write(cr, uid, product_ids, {'attribute_value_ids': [(4, variant_id.id)]}, context=ctx)

            # check product
            variant_ids_to_active = []
            variants_active_ids = []
            variants_inactive = []
            for product_id in tmpl_id.product_variant_ids:
                variants = sorted(map(int,product_id.attribute_value_ids))
                if variants in all_variants:
                    variants_active_ids.append(product_id.id)
                    all_variants.pop(all_variants.index(variants))
                    if not product_id.active:
                        variant_ids_to_active.append(product_id.id)
                else:
                    variants_inactive.append(product_id)
            if variant_ids_to_active:
                product_obj.write(cr, uid, variant_ids_to_active, {'active': True}, context=ctx)

            list_value = []
            #list_store = []
            # create new product
            for variant_ids in all_variants:
                #looping tmpl_id.tags to get "ID"
                for tag in tmpl_id.tags:
                    #append id many2many
                    list_value.append(tag.id)
                #looping tmpl_id.store to get "ID"
#                 for store in tmpl_id.store:
#                     #append id many2many
#                     list_store.append(store.id)
                values = {
                    'product_tmpl_id': tmpl_id.id,
                    'tags': [(6, 0, list_value)],
                    #'store': [(6, 0, list_store)],
                    'attribute_value_ids': [(6, 0, variant_ids)]
                }
                
                
                id = product_obj.create(cr, uid, values, context=ctx)
                variants_active_ids.append(id)

            # unlink or inactive product
            for variant_id in map(int,variants_inactive):
                try:
                    with cr.savepoint(), tools.mute_logger('openerp.sql_db'):
                        product_obj.unlink(cr, uid, [variant_id], context=ctx)
                #We catch all kind of exception to be sure that the operation doesn't fail.
                except (psycopg2.Error, except_orm):
                    product_obj.write(cr, uid, [variant_id], {'active': False}, context=ctx)
                    pass
        return True
    
    def create(self, cr, uid, vals, context=None):
        ''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
        product_template_id = super(product_template, self).create(cr, uid, vals, context=context)
        if not context or "create_product_product" not in context:
            self.create_variant_ids(cr, uid, [product_template_id], context=context)

        # TODO: this is needed to set given values to first variant after creation
        # these fields should be moved to product as lead to confusion
        related_vals = {}
        if vals.get('barcode'):
            related_vals['barcode'] = vals['barcode']
        if vals.get('default_code'):
            related_vals['default_code'] = vals['default_code']
        if vals.get('standard_price'):
            related_vals['standard_price'] = vals['standard_price']
        if vals.get('volume'):
            related_vals['volume'] = vals['volume']
        if vals.get('weight'):
            related_vals['weight'] = vals['weight']
        if related_vals:
            self.write(cr, uid, product_template_id, related_vals, context=context)

        return product_template_id
    
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(product_template, self).write(cr, uid, ids, vals, context=context)
        if 'attribute_line_ids' in vals or vals.get('active'):
            self.create_variant_ids(cr, uid, ids, context=context)
        #edit tags in object product.product
        if 'tags' in vals:
            ctx = context and context.copy() or {}
            ctx.update(active_test=False)
            product_ids = []
            for product in self.browse(cr, uid, ids, context=ctx):
                product_ids += map(int, product.product_variant_ids)
            self.pool.get("product.product").write(cr, uid, product_ids, {'tags': vals.get('tags')}, context=ctx)
        #edit store in object product.product
#         if 'store' in vals:
#             ctx = context and context.copy() or {}
#             ctx.update(active_test=False)
#             product_ids = []
#             for product in self.browse(cr, uid, ids, context=ctx):
#                 product_ids += map(int, product.product_variant_ids)
#             self.pool.get("product.product").write(cr, uid, product_ids, {'store': vals.get('store')}, context=ctx)
        if 'active' in vals and not vals.get('active'):
            ctx = context and context.copy() or {}
            ctx.update(active_test=False)
            product_ids = []
            for product in self.browse(cr, uid, ids, context=ctx):
                product_ids += map(int, product.product_variant_ids)
            self.pool.get("product.product").write(cr, uid, product_ids, {'active': vals.get('active')}, context=ctx)
        return res
    
    
class product_product(models.Model):
    _inherit = "product.product" 
    tags = fields.Many2many('product.brand',string="Tags")
    #store = fields.Many2many('pos.config',string="Store")

class CategoryShop(models.Model):
    _name = "category.shop"
    status = fields.Boolean('Active')
    Ads = fields.Text('Category Text')
    name = fields.Char('Name')

    @api.onchange('Ads')
    def _changes_categ(self):
        x = self.name
        categ_shop_ids = self.env['pos.config'].search([('category_shop', '=', x)])
        for categ in categ_shop_ids:
            categ.write({'ads':self.Ads})  


class ProductBrand(models.Model):
    _inherit = "product.brand"

    text = fields.Text(string="Brand Text")
