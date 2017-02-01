from openerp import fields, models, api


class PosOrder(models.Model):
    _inherit = "pos.order"

    is_max_reward = fields.Boolean(string="Is Maximum Reward")
    max_reward_value = fields.Float(string="Maximum Reward")

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        get_max_reward = ui_order['is_max_reward']
        order_fields['is_max_reward'] = get_max_reward
        if get_max_reward:
            order_fields['max_reward_value'] = ui_order['max_reward_value']
        return order_fields

    @api.depends('statement_ids', 'lines.price_subtotal_incl', 'lines.discount')
    def _compute_amount_all(self):
        super(PosOrder, self)._compute_amount_all()
        for order in self:
            order.amount_total = order.amount_total - order.max_reward_value
            if order.is_max_reward:
                currency = order.pricelist_id.currency_id
                order.amount_tax = currency.round((order.amount_total * (float(100)/float(110)) * 0.1))
