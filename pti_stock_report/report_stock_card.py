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

from openerp.osv import fields, osv
from openerp.tools.float_utils import float_compare, float_round
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import SUPERUSER_ID, api
import openerp.addons.decimal_precision as dp
from openerp.addons.procurement import procurement
import time
from datetime import datetime
class stock_move(osv.osv):
    _name = "stock.move"
    _inherit = ["stock.move"]
    _description = "Add messaging on stock move"
 
    def _get_desc(self, cr, uid, ids, fields, args, context=None):
        x = {}
        for b in self.browse(cr, uid, ids):
            if b.location_id.id == 8 and b.location_dest_id.id ==35: #supplier to stock
                x[b.id] = "Receive"
            elif b.location_id.id == 5 and b.location_dest_id.id == 35: #inventory loss to stock
                x[b.id] = "Receive2"
            elif b.location_id.id == 35 and b.location_dest_id.id == 8: #stock to supplier
                x[b.id] = "Reverse_Out"
            elif b.location_id.id == 35 and b.location_dest_id.id == 5: #stock to inventory loss
                x[b.id] = "Reverse_Out2"
            elif b.location_id.id == 7 and b.location_dest_id.id == 35: #production to stock
                x[b.id] = "Reverse"
#             elif b.location_id.id == 18 and b.location_dest_id.id == 35: #booked to stock
#                 x[b.id] = "Reverse2"
#             elif (b.location_id.id == 35 or b.location_id.id == 18) and b.location_dest_id.id == 7: #booked to production OR stock to production
            elif b.location_id.id == 35 and b.location_dest_id.id == 7: #stock to production
                x[b.id] = "Consume"    
            else:    
                x[b.id] = ""
        return x
    
    def _get_date_stock(self, cr, uid, ids, fields, args, context=None):
            x = {}
            for b in self.browse(cr, uid, ids):
                if b.date :
                    value = b.picking_id.date_done
                    x[b.id] = value
                else:    
                    x[b.id] = ""
            return x   
            
    _columns = {
            'transaction_desc': fields.function(_get_desc, type= 'char', string='Transaction Description'),
            'date_track'    : fields.function(_get_date_stock, type='date', string='Date',store=True),
    }
stock_move()
