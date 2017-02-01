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
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError

class account_register_payments(models.TransientModel):
    _inherit = 'account.register.payments'
    _description = "Add on change on payment method"

    @api.onchange('payment_method_id')
    def _onchange_payment_method(self):
        self.payment_method_code = self.payment_method_id.code

class accountPayment(models.Model):
    _inherit = "account.payment"
    
    def _get_counterpart_move_line_vals(self, invoice=False):
        res = super(accountPayment, self)._get_counterpart_move_line_vals(invoice)
        if invoice:
            res['invoice_id'] = invoice.id
            res['partner_id'] = invoice.partner_id.id
        return res

