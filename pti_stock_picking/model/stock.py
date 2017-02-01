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
from datetime import date, datetime
from dateutil import relativedelta
from openerp.osv import fields, osv
from openerp import models, fields, api, _
from openerp.exceptions import UserError
import logging
from openerp.exceptions import except_orm, Warning, RedirectWarning
_log = logging.getLogger(__name__)

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    @api.one
    def _compute_sendback(self):
        send_back=False
        in_orgin=self.env['stock.picking'].search(['|',('origin','=',self.name),('name','=',self.origin)])
        if in_orgin:
            send_back=True
        self.is_send_back=send_back
        
    @api.one
    def _compute_is_retur_type(self):
        is_type=self.env['stock.picking.type'].search([('id','=',self.picking_type_id.id)])
        self.is_retur_type=is_type.is_retur
            
    retur_reason = fields.Many2one('retur.reason','Retur Reason')
    flag_cust=fields.Selection(string='related location',related='location_id.usage')
    is_send_back=fields.Boolean(string='is send back', compute='_compute_sendback')
    is_retur_type=fields.Boolean(string='is_retur',compute='_compute_is_retur_type')
    is_retur = fields.Boolean ('Retur', compute='take_retur_value')
    is_have_cn = fields.Boolean ('account credit note', compute='_take_origin_cn')
    
    @api.one
    @api.depends('name')
    def _take_origin_cn(self):
        x = self.env['account.invoice'].search([('origin','=',self.name)])
        if self.name == x.origin:
            self.is_have_cn = True
        else:
            self.is_have_cn = False
    
    @api.one
    @api.depends('picking_type_id.is_retur')
    def take_retur_value(self):
        for this in self:
            if this.picking_type_id.is_retur == True:
                this.is_retur = this.picking_type_id.is_retur
                
    @api.multi
    def action_finish_update(self):
        for line in self.pack_operation_product_ids:
            if line.qty_done == 0:
                line.write({'qty_done':line.product_qty})
        return True
    
    @api.model
    def create(self, values):
        if not values.get('partner_id'):
            if values.get('location_dest_id'):
                loc = self.env['stock.location'].browse([values['location_dest_id']])
                if loc.partner_id.id:
                    status = loc.partner_id.is_consignment or loc.partner_id.is_team_leader
                    if status:
                        values['partner_id'] = loc.partner_id.id
                    else:
                        values['partner_id'] = loc.partner_id.id
        return super(stock_picking, self).create(values)

class stock_picking_warning(osv.osv):
    _inherit = 'stock.picking'

    def action_assign_warning(self, cr, uid, ids, context=None):
        """ Check availability of picking moves.
        This has the effect of changing the state and reserve quants on available moves, and may
        also impact the state of the picking as it is computed based on move's states.
        @return: True
        """
        for pick in self.browse(cr, uid, ids, context=context):
            if pick.state == 'draft':
                self.action_confirm(cr, uid, [pick.id], context=context)
            #skip the moves that don't need to be checked
            move_ids = [x.id for x in pick.move_lines if x.state not in ('draft', 'cancel', 'done')]
            if not move_ids:
                raise UserError(_('Nothing to check the availability for.'))
            self.pool.get('stock.move').action_assign(cr, uid, move_ids, context=context)
            if pick.state == "confirmed":
                raise Warning("Cannot do booking as stock is not available, please cancel Delivery Order and Set SO as set to done then inform to management incharge")
        return True

