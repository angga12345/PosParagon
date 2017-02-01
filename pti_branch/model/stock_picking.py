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
from openerp.exceptions import UserError
import logging
_log = logging.getLogger(__name__)
from openerp import SUPERUSER_ID

class stockPicking(models.Model):
    _inherit = "stock.picking"
    
    can_view = fields.Boolean(compute="_compute_access", search="_search_can_view")

    def _search_can_view(self, operator, value):
        if operator not in ('=','!=','<>'):
            raise UserError(_("operator invalid!"))
        if self._uid == SUPERUSER_ID:
            return [(1,'=',1)]
        dc_ids = False
        dc_id = False
        dc_id = self.env.user.partner_id.dc_id.id
        if not self.env.user.partner_id.warehouse_ids and not dc_id:
            return [(1,'=',1)]
        else:
            warehouses = self.env.user.partner_id.warehouse_ids
            dc_ids = tuple([wh.dc_id.id for wh in warehouses if wh.dc_id.id])
        if dc_id:
            req = """
                select id from stock_picking where
                    location_id in (select id from stock_location where dc_id = %d)
                    or
                    location_dest_id in (select id from stock_location where dc_id = %d)
            """
            self.env.cr.execute(req % (dc_id, dc_id))
        elif dc_ids:
            if len(dc_ids)==1:
                dc_id = dc_ids[0]
                req = """
                    select id from stock_picking where
                        location_id in (select id from stock_location where dc_id = %d)
                        or
                        location_dest_id in (select id from stock_location where dc_id = %d)
                """
                self.env.cr.execute(req % (dc_id, dc_id))
            else:
                req = """
                    select id from stock_picking where
                        location_id in (select id from stock_location where dc_id in %s)
                        or
                        location_dest_id in (select id from stock_location where dc_id in %s)
                """
                self.env.cr.execute(req % (dc_ids, dc_ids))
        else:
            return [(1,'=',1)]

        
        ids = [i[0] for i in self.env.cr.fetchall()]
        op = operator == '=' and "in" or "not in"
        return [('id', op, ids)]

    @api.multi
    def _compute_access(self):
        dc_user = self.env.user.partner_id.dc_id.id
        for picking in self:
            if picking.location_id.dc_id.id == dc_user or picking.location_dest_id.dc_id.id == dc_user:
                picking.can_view = True

    # super function action_confirm to display warning when mark as todo but product still none
    def action_confirm(self, cr, uid, ids, context=None):
        res = super(stockPicking, self).action_confirm(cr, uid, ids, context=context)

        for picking in self.browse(cr, uid, ids, context=context):
            if not picking.move_lines:
                raise UserError(_("You should fill minimum 1 product before mark as todo."))
        return res
