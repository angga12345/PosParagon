from openerp import models, fields, api, _

# class PurchaseOrderLine(models.Model):
#     _inherit = "purchase.order.line"
#
#     @api.multi
#     def _get_state_purchase(self):
#         purchase = self.env['purchase_order'].browse(self.order_id)
#         self.state_purchase = purchase.state
#
#     state_purchase = fields.Char(compute=_get_state_purchase, string='State', store=True)
#
