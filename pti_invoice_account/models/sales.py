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

class SalesOrder(models.Model):
    _inherit = "sale.order"
    
    @api.multi
    def _prepare_invoice(self):
        res = super(SalesOrder, self)._prepare_invoice()
        res.update({'type_code_invoice' : '20' if self.partner_id.is_team_leader or self.partner_id.is_consignment else '10'})
        return res

