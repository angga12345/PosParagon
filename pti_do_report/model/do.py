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

import pytz
from openerp import SUPERUSER_ID
from datetime import datetime, timedelta
from openerp import models, fields, api, _
from openerp.tools import float_is_zero
from openerp.exceptions import UserError

class stock_picking(models.Model):
    _inherit = "stock.picking"
    
    @api.model
    def _get_time(self):
        now = datetime.now()
        return now
     
    total_amount=fields.Float(string='DO Value (exc.Discount)', compute='_get_total_amount')
    notes = fields.Text('Terms and Conditions')
    notif_report_printed = fields.Boolean('Printed', default=False)
    proforma_printed = fields.Boolean('Proforma Printed', default=False)
    date_create_do = fields.Datetime('time create DO', default=_get_time)
    term_of_delivery_time = fields.Char()
    consignment = fields.Boolean(compute='CheckDeliveryType', string='Is Delivery Consignment', default=True)
    proforma_number = fields.Char('Proforma number')
    ########## rename string from printed to printed based because same string with notif report printed ##########
    printed = fields.Boolean('Printed Base')

    @api.one
    def _get_total_amount(self):
        get_id=self.id
        tot=0
        for move in self.move_lines:
            price = move.product_id.list_price
            qt=move.product_qty
            tot +=price * qt

        self.total_amount=tot


    @api.depends('partner_id')
    def CheckDeliveryType(self):
        for do in self:
            if do.partner_id.id:
                if do.partner_id.is_team_leader or do.partner_id.is_consignment:
                    do.consignment = True
            else:
                do.consignment = True
        
    def do_print_proforma_invoice(self, cr, uid, ids, context=None):
        context = dict(context or {}, active_ids=ids)
        stock_pick = self.pool.get('stock.picking').browse(cr, uid, ids, context=context)
        for data in stock_pick:
            self.write(cr, uid, data.id, {'proforma_number' : 'PFI/' + data.name}, context=context)
        return self.pool.get("report").get_action(cr, uid, ids, 'pti_do_report.report_pi', context=context)

