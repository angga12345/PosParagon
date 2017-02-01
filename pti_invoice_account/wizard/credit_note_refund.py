# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.tools.safe_eval import safe_eval as eval
from openerp.exceptions import UserError
from openerp.osv import osv
import logging
_logger = logging.getLogger(__name__)

class AccountInvoiceRefund(models.TransientModel):
    """Refunds invoice"""

    _inherit = "account.invoice.refund"
            
    @api.multi
    def compute_refund_credit(self, mode='refund'):
        inv_obj = self.env['account.invoice']
        context = dict(self._context or {})
        for form in self:
            created_inv = []
            date = False
            description = False
            for inv in inv_obj.browse(context.get('active_ids')):
                if inv.state in ['draft', 'proforma2', 'cancel']:
                    raise UserError(_('Cannot refund draft/proforma/cancelled invoice.'))
                if inv.reconciled:
                    raise UserError(_('Cannot refund invoice which is already reconciled, invoice should be unreconciled first. You can only refund this invoice.'))

                date = form.date or False
                description = form.description or inv.name
                refund = inv.refund(form.date_invoice, date, description, inv.journal_id.id)
                refund.compute_taxes()

                created_inv.append(refund.id)
                movelines = inv.move_id.line_ids
                to_reconcile_ids = {}
                to_reconcile_lines = self.env['account.move.line']
                for line in movelines:
                    if line.account_id.id == inv.account_id.id:
                        to_reconcile_lines += line
                        to_reconcile_ids.setdefault(line.account_id.id, []).append(line.id)
                    if line.reconciled:
                        line.remove_move_reconcile()
                refund.signal_workflow('invoice_open')
                for tmpline in refund.move_id.line_ids:
                    if tmpline.account_id.id == inv.account_id.id:
                        to_reconcile_lines += tmpline
                        to_reconcile_lines.reconcile()
                ######### set state for cancelation credit note #########
                refund_cn = inv.write({'state_refund': 'refund'})
                refund_cn = refund.write({'state_refund': 'done'})

                # Put the reason in the chatter
                subject = _("Invoice refund")
                body = description
                refund.message_post(body=body, subject=subject)

        return refund_cn

    @api.multi
    def invoice_refund_credit(self):
        invoices= self.env.context.get('active_ids')
        credit_note= self.env['account.invoice.refund'].browse(invoices)
        data_refund = self.read(['filter_refund'])[0]['filter_refund']
        self.compute_refund_credit(credit_note)
    
