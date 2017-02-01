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

from openerp import models, fields, api, _

class confirm_box(models.TransientModel):
    _inherit = 'confirm_box'

    @api.multi
    def continue_process(self):
        self.ensure_one
        vals = {
            'sale_order_id': self._context['sales_order_id'],
            'bypass_time': fields.Datetime.now(),
            'user_id': self._context['uid']
        }
        history_id = self.env['sale.order.bypasslimit.history'].create(vals)
        sale = self.env['sale.order'].browse([self._context['sales_order_id']])
        sale.with_context({'checked' : True}).quick_action_confirm()
        return True

