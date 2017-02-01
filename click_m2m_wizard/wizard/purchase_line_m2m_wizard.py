from openerp import models, fields, api, _
from openerp.exceptions import UserError

class purchase_order_line_wizard(models.TransientModel):
    _name = 'purchase.order.line.wizard'

    def set_taxes(self):
        active_id = self.env.context.get('active_id')
        po_line_obj = self.env['purchase.order.line'].browse(active_id)
        tax = []
        tax = [t.id for t in po_line_obj.taxes_id]
        return [(6, 0, tax)]
        
    taxes = fields.Many2many('account.tax', string='Tax', default=set_taxes)
    apply_all = fields.Boolean('Aply to all lines', default=False)

    @api.multi
    def apply_changes(self):
        active_id = self.env.context.get('active_id')
        po_line_obj = self.env['purchase.order.line'].browse(active_id)
        purchase = po_line_obj.order_id
        if purchase.state == 'draft':
            taxes = [t.id for t in self.taxes]
            if self.apply_all:
                for line in purchase.order_line:
                    line.write({
                        'taxes_id': [(6, 0, taxes)]
                    })
            else:
                po_line_obj.write({
                    'taxes_id': [(6, 0, taxes)]
                })
        else:
            raise UserError(_("Purchase already confirm."))
