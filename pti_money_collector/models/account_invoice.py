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

from openerp import models, api, fields
from operator import itemgetter

import logging
_log = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def write(self, vals):
        if vals.get('collector_id', False):
            make_log = 'Invoice hold by Collector %s ' % self.env['res.partner'].browse(vals['collector_id']).name
            self.sudo().message_post(body=make_log)
        else:
            if self.collector_id:
                make_log='Collectors %s bring the invoice back to Sales Admin' % self.collector_id.name
                self.sudo().message_post(body=make_log)

        result = super(AccountInvoice, self).write(vals)
        return result
            

