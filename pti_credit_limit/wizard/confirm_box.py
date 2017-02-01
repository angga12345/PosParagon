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
    _name = 'confirm_box'
    _description = 'confirm_box'
    _req_name = 'title'

    title = fields.Char(
        string="Title",
        size=100,
        readonly=True
        )
    message = fields.Text(
        string="Message",
        readonly=True
        )

    @api.multi
    def message_action(self):
        self.ensure_one
        res = {
            'name': '%s' % (_(self.title)),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env['ir.model.data'].xmlid_to_res_id('credit_limit.confirm_box_form'),
            'res_model': 'confirm_box',
            'domain': [],
            'context': self._context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id
        }
        return res

    @api.model
    def confirm(self, title, message):
        record = self.create({
            'title': title,
            'message': message})
        return record.message_action()

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
        sale.with_context({'checked' : True}).action_confirm()
        return True

