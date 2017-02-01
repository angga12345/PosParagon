from openerp import models, fields, api, _
from openerp.exceptions import UserError

class invoice_line_wizard(models.TransientModel):
    _name = 'invoice.line.wizard'

    options = fields.Selection([
        ('discount', 'Discount'),
        ('taxes', 'Taxes')
    ], string='What to update :', default='discount')
    active_id = fields.Integer(string='Active ID :',
                               default=lambda self: self.env.context['active_id'])  # DISPLAY ID OF SELECTED ITEM

    @api.one
    @api.onchange('options')
    def onchange_option(self):
        invoice_line_obj = self.env['account.invoice.line'].browse(self.active_id)
        disc = []
        tax = []
        disc = [d.id for d in invoice_line_obj.discount_m2m]
        self.update({'discount_m2m': [(6, 0, disc)]})
        tax = [t.id for t in invoice_line_obj.invoice_line_tax_ids]
        self.update({'taxes': [(6, 0, tax)]})

    discount_m2m = fields.Many2many('discount.discount', string='Discounts')
    taxes = fields.Many2many('account.tax', string='Tax')
    apply_all = fields.Boolean('Aply to all lines', default=False)

    @api.multi
    def apply_changes(self):
        self.ensure_one()
        invoice_line_obj = self.env['account.invoice.line'].browse(self.active_id)
        if invoice_line_obj.invoice_id.state == 'draft':
            disc = [d.id for d in self.discount_m2m]
            taxes = [t.id for t in self.taxes]
            if self.apply_all:
                lines = invoice_line_obj.invoice_id.invoice_line_ids
                for line in lines:
                    line.write({
                    'discount_m2m': [(6, 0, disc)],
                    'invoice_line_tax_ids': [(6, 0, taxes)]
                })

            else:
                invoice_line_obj.write({
                    'discount_m2m': [(6, 0, disc)],
                    'invoice_line_tax_ids': [(6, 0, taxes)]
                })
            invoice_line_obj.invoice_id._update_taxes()
        else:
            raise UserError(_("Invoice already validated."))