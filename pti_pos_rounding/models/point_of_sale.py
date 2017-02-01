from openerp import models, fields, api


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _amount_line_tax(self, cr, uid, line, fiscal_position_id, context=None):
        taxes = line.tax_ids.filtered(lambda t: t.company_id.id == line.order_id.company_id.id)
        if fiscal_position_id:
            taxes = fiscal_position_id.map_tax(taxes)
        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        cur = line.order_id.pricelist_id.currency_id
        taxes = taxes.compute_all(price, cur, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)['taxes']
        val = 0.0
        for c in taxes:
            val += c.get('amount', 0.0)
        return val

    amount_tax = fields.Float(compute='_compute_amount_all', string='Taxes', digits=0)
    amount_total = fields.Float(compute='_compute_amount_all', string='Total', digits=0)
    amount_paid = fields.Float(compute='_compute_amount_all', string='Paid', states={'draft': [('readonly', False)]}, readonly=True, digits=0)
    amount_return = fields.Float(compute='_compute_amount_all', string='Returned', digits=0)

    @api.depends('statement_ids', 'lines.price_subtotal_incl', 'lines.discount')
    def _compute_amount_all(self):
        for order in self: 
            order.amount_paid = order.amount_return = order.amount_tax = 0.0
            currency = order.pricelist_id.currency_id
            order.amount_paid = sum(payment.amount for payment in order.statement_ids)
            order.amount_return = sum(payment.amount < 0 and payment.amount or 0 for payment in order.statement_ids)
            order.amount_tax = currency.round(sum(self._amount_line_tax(line, order.fiscal_position_id) for line in order.lines))
            amount_untaxed = currency.round(sum(line.price_subtotal_incl for line in order.lines))
            global_disc = order.membership_global_disc / 100
            order.amount_total = (amount_untaxed - (amount_untaxed * global_disc))