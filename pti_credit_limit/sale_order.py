# Copyright (C) 2016 by PT Paragon Technology And Innovation
#
# This file is part of PTI Odoo Addons.
#
# PTI Odoo Addons is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PTI Odoo Addons is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with PTI Odoo Addons.  If not, see <http://www.gnu.org/licenses/>.

from openerp import api, fields, models, _
from openerp import SUPERUSER_ID
from openerp.exceptions import UserError, ValidationError
from openerp.osv import fields, osv

class sale_order(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_confirm(self):
        context = self._context or False
        if not context.get('checked',False):
#             for so_line in self.order_line:
#                 prod_src = self.env['sale.order.line'].search([('product_id','=',so_line.product_id.id),('order_id','=',self.id), ('is_free','=',so_line.is_free)])
#                 if len(prod_src) > 1:
#                     raise osv.except_osv(_(''), _('Sorry, you have same product.'))                
    
            partne_obj = self.env['res.partner']
            MAX_DEPTH = 1
            # this code will handle partner with depth 2 level only
            partner_sudo = partne_obj.sudo().search([('id','=',self.partner_id.id)])
            list_partner = []
            root = self.searchRoot(partner_sudo, MAX_DEPTH)
            # i decided for child max 1 level depth based on master data customer
            # but if need more we can improve (Keep it simple)
            list_partner.append(root.child_ids)
            list_partner.append(root)
            credit = self.count_all(list_partner) # count all invoice related with partner
            available_credit = self.partner_id.credit_limit - \
                                self.partner_id.credit - \
                                credit
    
            if self.amount_total > available_credit:
                title = 'Credit Over Limits!'
                msg = u'Can not confirm the order since the credit balance is %s.' % (available_credit,)
                return self.env['confirm_box'].with_context(sales_order_id=self.id).confirm(title, msg)
            else:
                self.button_dummy()
                super(sale_order,self).action_confirm()
        else:
            self.button_dummy()
            super(sale_order,self).action_confirm()

    def searchRoot(self, partner_id, depth):
        if not partner_id.parent_id.id or depth == 0:
            return partner_id
        else:
            depth = depth - 1
            return self.searchRoot(partner_id.parent_id, depth)
    
    def count_sale_invoiced(self):
        invoice_ids = self.order_line.mapped('invoice_lines').mapped('invoice_id')
        # Search for refunds as well
        refund_ids = self.env['account.invoice'].browse()
        if invoice_ids:
            refund_ids = refund_ids.search([('type', '=', 'out_refund'), ('origin', 'in', invoice_ids.mapped('number'))])
        return len(set(invoice_ids.ids + refund_ids.ids))
    
    def count_all(self, list_partner):
        account_invoice_obj = self.env['account.invoice']
        credit_inv = 0
        for all_ids in list_partner:
            for partner in all_ids:
                list_inv = account_invoice_obj.sudo().search([('partner_id','=',partner.id),
                                                              ('state', 'in', ('draft','open'))])
                # sum invoice not yet paid
                # only validated invoice
                for inv in list_inv:
                    if inv.state != 'draft':
                        credit_inv += inv.residual_signed
                    else:
                        credit_inv += inv.amount_total_signed
                
                sales = self.sudo().search([('partner_id','=',partner.id),('state','in',('done','sale'))])
                # sum amount total SO not yet invoiced
                for data_sale in sales:
                    if data_sale.count_sale_invoiced()==0:
                        credit_inv += data_sale.amount_total
                    
        return credit_inv

