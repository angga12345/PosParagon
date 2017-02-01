from openerp import api, fields, models, _
from openerp.exceptions import except_orm


class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            invoice_id = {}
            if invoice.partner_id.journal_id.name == 'Sales Parama':
                partner_obj = self.env['res.partner'].search([('name','=','Parama')])
                invoice_line = self.invoice_line_ids
                invoice_line_ids = [x.id for x in invoice_line]
                if invoice_line_ids:
                    invoice_id = invoice.copy(default={
                        'name': '/',
                        'partner_id':partner_obj[0].id,
                        'type_code_invoice': '40',
                        'type':'out_refund',
                        'state_refund':False,
                        'journal_id':partner_obj[0].journal_id.id,
                    })
                    invoice_id.message_post(body=_("This credit note was created on behalf of document: %s") % (invoice.number))
                    invoice_id.action_date_assign()
                    invoice_id.action_move_create()
                    invoice_id.invoice_validate()
                invoice.message_post(body=_("On behalf of this document was created new document: %s") % (invoice_id.number))
        return res


            