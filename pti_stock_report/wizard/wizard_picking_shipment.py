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

class wizard_picking_shipment(models.TransientModel):
    _name = 'picking.to.shipment'
    
    tracking_id = fields.Many2one('truck.picking.shipment', 'Picking Shipment', required=True)

    def picking_shipment(self, cr, uid, ids, context=None):
        #use active_ids to add picking line to the selected shipment
        tracking_id = self.browse(cr, uid, ids, context=context)[0].tracking_id.id
        picking_ids = context.get('active_ids', False)
        filtered_ids = False
        if picking_ids:
            picking_ids = tuple(picking_ids)
            cr.execute("select sp.id from stock_picking sp join stock_picking_type spt on picking_type_id=spt.id where sp.id in %s and sp.state = 'done' and spt.name = 'Delivery Orders' and (sp.state_shipment = 'pending' or sp.state_shipment = 'cancel' or sp.tracking_id is null)", (picking_ids,))
            temporary = cr.fetchall()
            if temporary:
                filtered_ids = [d[0] for d in temporary]
                
        if not filtered_ids:
            return
        return self.pool.get('stock.picking').write(cr, uid, filtered_ids, {'tracking_id': tracking_id, 'state_shipment':'draft'})
        