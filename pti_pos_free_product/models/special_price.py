from openerp import fields, models, api
 
 
class PosOrder(models.Model):
    _inherit = 'pos.order'

    special_price = fields.Float(string='Special Price')

    def _get_total_without_special_price(self, order):
        subtotal = 0
        for po_line in order.lines:
            if not po_line.is_special_price:
                subtotal += po_line.price_subtotal_incl
        return subtotal

    @api.depends('statement_ids', 'lines.price_subtotal_incl', 'lines.discount')
    def _compute_amount_all(self):
        amount_all = super(PosOrder, self)._compute_amount_all()
        for order in self:
            subtotal = self._get_total_without_special_price(order)
            if order.special_price > 0:
                order.amount_total = subtotal + order.special_price
            for line in order.lines:
                if line.is_special_price:
                    currency = order.pricelist_id.currency_id
                    order.amount_tax = currency.round((order.amount_total * (float(100)/float(110)) * 0.1))
                break

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        order_fields['special_price'] = ui_order['special_price']
        return order_fields


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    is_special_price = fields.Boolean(string='Get Special Price')
