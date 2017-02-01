from openerp import models, fields, api, _


class Pricelists(models.Model):
    _inherit = 'product.pricelist.item'

    percent_price = fields.Float(string='Percentage Price')
    discount_pti = fields.Float(string='Discount PTI')
    discount_mds = fields.Float(string='Discount MDS')

    @api.onchange('discount_pti', 'discount_mds')
    def onchange_discount(self):
        self.percent_price = self.discount_pti + self.discount_mds

    @api.model
    def create(self, values):
        values['percent_price'] = values['discount_pti'] + values['discount_mds']
        return super(Pricelists, self).create(values)

    @api.multi
    def write(self, values):
        for rec in self:
            values['percent_price'] = values.get('discount_pti', rec.discount_pti) + values.get('discount_mds', rec.discount_mds)
        return super(Pricelists, self).write(values)
