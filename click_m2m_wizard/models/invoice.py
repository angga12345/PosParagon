from openerp import models, fields, api, _

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.one
    def _update_taxes(self):
        taxes_grouped = self.get_taxes_values()
        tax_lines = self.tax_line_ids.browse([])
        for tax in taxes_grouped.values():
            tax_lines += tax_lines.new(tax)
        self.tax_line_ids = tax_lines
        return

# class AccountInvoiceLine(models.Model):
#     _inherit = "account.invoice.line"
#
#     @api.multi
#     @api.depends('invoice_id.state')
#     def _get_state_invoice(self):
#         for line in self:
#             line.state = line.invoice_id.state
#
#     state_inv = fields.Char(compute=_get_state_invoice, string='State', store=True, default='draft')
