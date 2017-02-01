from openerp import models, fields, api, _
from openerp.exceptions import UserError
import logging
_log = logging.getLogger(__name__)


class product_product(models.Model):
    _inherit = "product.product"

    voucher = fields.Boolean('Is a Voucher')
    start_date = fields.Date('Start Date', help="Starting date for the voucher")
    end_date = fields.Date('End Date', help="Ending date for the voucher")

    @api.model
    def create(self, values):
        product_id = super(product_product, self).create(values)
        if product_id.product_tmpl_id:
            product_id.write({
                'voucher': product_id.product_tmpl_id.voucher,
                'start_date': product_id.product_tmpl_id.start_date,
                'end_date': product_id.product_tmpl_id.end_date,
            })
        return product_id

    @api.onchange('voucher')
    def _onchange_voucher(self):
        self.taxes_id, self.supplier_taxes_id = None, None


class product_template(models.Model):
    _inherit = "product.template"

    voucher = fields.Boolean('Is a Voucher')
    start_date = fields.Date('Start Date', help="Starting date for the voucher")
    end_date = fields.Date('End Date', help="Ending date for the voucher")

    @api.onchange('voucher')
    def _onchange_voucher(self):
        self.taxes_id, self.supplier_taxes_id = None, None
