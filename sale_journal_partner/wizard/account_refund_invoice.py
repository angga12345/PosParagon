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

# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.tools.safe_eval import safe_eval as eval
from openerp.exceptions import UserError

class AccountInvoiceRefund(models.TransientModel):
    _inherit = "account.invoice.refund"

    @api.multi
    def compute_refund(self, mode):
        res = super(AccountInvoiceRefund, self).compute_refund(mode)
        inv_obj = self.env['account.invoice']
        context = dict(self._context or {})

        for form in self:
            for inv in inv_obj.browse(context.get('active_ids')):
                refund_ids = inv_obj.search([('origin','=',inv.number)])
                if refund_ids[0].journal_id.name == 'Sales Parama':    
                    if mode in ('cancel', 'modify'):
                        if form.invoice_already_send == True:
                            if 'PRM/' in refund_ids[0].number:
                                new_number = refund_ids[0].number.replace('PRM/','')
                                refund_ids[0].write({'number': 'PRM/' + new_number })
        return True