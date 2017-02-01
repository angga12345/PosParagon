from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_dummy_product = fields.Boolean(string="Is Dummy Product")
