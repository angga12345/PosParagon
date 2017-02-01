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
from openerp.exceptions import UserError


class truck_pti(models.Model):
    _inherit = 'truck.pti'

    dc_id = fields.Many2one('res.partner', 'DC')


class truck_picking_shipment(models.Model):
    _inherit = 'truck.picking.shipment'

    @api.model
    def _default_dc(self):
        return self.env.user.partner_id.dc_id

    dc_id = fields.Many2one('res.partner', 'DC', default=_default_dc)