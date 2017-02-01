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
from datetime import datetime

class truck_pti(models.Model):
    _name = 'truck.pti'
         
    name = fields.Char('Nomor Plat', required = True,)  
    
    @api.multi
    def write(self,vals):
        """This function super using for deleting space and 
        make text to caps lock if edit Truck"""
        if vals.get('name'):
            name_val=vals['name']
            name_val=name_val.replace(" ","")
            vals['name']=name_val.upper()
        res=super(truck_pti,self).write(vals)
        return res
    
    @api.model
    def create(self,vals):
        """This function super using for deleting space and 
        make text to caps lock if create Truck"""
        if vals.get('name'):
            name_val=vals['name']
            name_val=name_val.replace(" ","")
            vals['name']=name_val.upper()
        res=super(truck_pti,self).create(vals)
        return res


class truck_picking_shipment(models.Model):
    _name = 'truck.picking.shipment'
    
    @api.model
    def _default_user(self):
        return self.env.user
    
    name = fields.Char('Shipping Name', required=True,default='/', copy=False)
    user_id = fields.Many2one('res.users', 'User',default=_default_user)
    truck_id = fields.Many2one('truck.pti', 'Truck')
    picking_ids = fields.One2many('stock.picking', 'tracking_id', string='Pickings',
        readonly=False, states={'in_progress': [('readonly', True)],
                                'done': [('readonly', True)],
                                'cancel': [('readonly', True)]})
    partner_id = fields.Many2one('res.partner', 'Driver')
    state = fields.Selection([('draft', 'Draft'), ('in_progress', 'Running'), ('done', 'Done'), ('cancel', 'Cancelled')], string="State", required=True, default="draft")    
    date_shipment = fields.Datetime('Date Shipment', required=True, default=lambda self: fields.datetime.now())
    
    @api.multi
    def confirm_tracking(self):
        for shipment in self:
            if not shipment.picking_ids:
                raise UserError(_("Please fill picking before confirm!"))
            found = self.search([('truck_id', '=', shipment.truck_id.id), ('state','=','in_progress')], limit=1)
            if found:
                msg = "Truck %s is on the way. Please check shipment %s" % (shipment.truck_id.name, found.name)
                raise UserError(_(msg))
            for line in shipment.picking_ids:
                if line.state_shipment == 'draft':
                    line.write({'state_shipment':'in_progress'})
            self.write({'state': 'in_progress'})
        return True

    @api.multi
    def done_tracking2(self):
        """This function for set state to be done, set date shipment and set state shipment"""
        for line in self.picking_ids:
            if line.state_shipment == 'in_progress':
                line.write({'state_shipment':'done', 'date_shipment_picking': self.date_shipment})
            else:
                line.write({'date_shipment_picking': self.date_shipment})
        self.write({'state': 'done'})
        return True    

    @api.multi
    def done_tracking(self):
        view_id = self.env.ref(
            'pti_stock_report.view_done_shipment')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'truck.picking.shipment',
            'view_id': view_id.id,
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            }
            
    @api.multi
    def cancel_tracking(self):
        for line in self.picking_ids:
            if line.state_shipment == 'in_progress':
                line.write({'state_shipment':'cancel'})
        self.write({'state': 'cancel'})
        return True
    
    @api.multi
    def set_all_done(self):
        for line in self.picking_ids:
            if line.state_shipment == 'in_progress':
                line.write({'state_shipment':'done'})
        return True

    @api.model
    def create(self, vals):
        """This function for numbering shipment"""
        if vals.get('name', '/') == '/':
            res=self.env['res.users'].search([('id','=',self._uid)],limit=1)
            a = res.partner_id.dc_id.ref
            code = self.env['ir.sequence'].next_by_code('picking.shipment.new')
            split_codes = code.split('/')
            if a == False :
                raise UserError(_("You do not have ref number"))
            else :
                result = ''
                if len(split_codes) > 1:
                    result = split_codes[0] + '/' + a + '/' + split_codes[1]            
            vals['name'] = result or '/'
        return super(truck_picking_shipment, self).create(vals)
    
    @api.multi
    def print_picking(self):
        return self.env['report'].get_action(self, 'pti_do_report.report_tracking_shipment')
    
class stock_picking(models.Model):
    _inherit = "stock.picking"
         
    tracking_id = fields.Many2one('truck.picking.shipment', 'Picking Shipment', copy=False)
    state_shipment = fields.Selection([('draft', 'Draft'), ('in_progress', 'Running'), ('pending', 'Pending'), ('done', 'Done'), ('cancel', 'Cancelled')], string='State Shipment', copy=False)
    date_shipment_picking = fields.Datetime('Date Shipment Picking')
    
    @api.one
    def set_state_shipment_pending(self):
        '''
        FOR USER STOCK, DO branch 
        '''
        if self.state_shipment == 'in_progress':
            res = self.write({'state_shipment':'pending'})
        return res
    
    @api.one
    def set_state_shipment_done(self):
        '''
        FOR USER STOCK, DO branch 
        '''
        if self.state_shipment == 'in_progress':
            res = self.write({'state_shipment':'done'})
        return res

    @api.multi
    def write(self, values):
        for pick in self:
            if values.get('tracking_id') and pick.state == 'done':
                values['state_shipment'] = 'draft'
                msg = "State Shipment : %s" % pick.state_shipment
                pick.message_post(body=msg)        
        res = super(stock_picking, self).write(values)
        return res
    
    @api.one
    def set_state_shipment_dones(self):
        self.write({'state_shipment': 'done'})
    
    @api.one
    def set_state_shipment_cancel(self):
        self.write({'state_shipment': 'cancel'})

    @api.one
    def set_state_shipment(self):
        self.write({'state_shipment': 'pending'})

    @api.multi
    def delete_only_one_line(self):
        self.update({'state_shipment' : False})
        self.update({'tracking_id' : False})
        return {'type': 'ir.actions.client','tag': 'reload',}

class res_partner(models.Model):
    _inherit="res.partner"
    
    is_driver = fields.Boolean('Is Driver',default=False)