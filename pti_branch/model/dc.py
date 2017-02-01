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

class partner(models.Model):
    _inherit = "res.partner"
    
    @api.model
    def set_default_dc(self):
        print("hahahahahha >>>>>",self.env.user.partner_id.dc_id)
        return self.env.user.partner_id.dc_id 

    @api.model
    def _search_user_dc(self, operator, operand):
        """Search function for user_ids
        only search by user id
        """
        self._cr.execute("select rp.dc_id from res_users ru inner join res_partner rp "\
            "on rp.id=ru.partner_id "\
            "where ru.id=%s", (operand,))
        ress = self._cr.fetchall()
        dc_ids = []
        for res in ress:
            dc_ids.append(res[0])

        return [('id', 'in', dc_ids)]

    @api.multi
    def _compute_user_dc(self):
        dc = self[0].dc_id
        self._cr.execute("SELECT id FROM res_users WHERE partner_id = %s", (self[0].id or None, ))
        user_exist = self._cr.fetchone()
        if user_exist:
            self._cr.execute("SELECT id FROM res_users WHERE partner_id IN (SELECT id FROM res_partner WHERE dc_id = %s)", (self[0].id or None, ))
            all_users2 = self._cr.fetchall()
            dc.user_ids = [(6, 0, all_users2)       ]

    # HIDE expired date sale.order
    dc_id = fields.Many2one('res.partner','Distribution Center', domain=[('is_dc','=',True)], help='Distribution center', default=lambda self: self.set_default_dc())
    is_dc = fields.Boolean('Is a Distribution Center', help="Check this box if this partner is a distribution center.")
    is_employee = fields.Boolean('Is employee')
    this_for_all = fields.Boolean('This for all')
#     user_ids = fields.Many2many('res.users', compute='_compute_user_dc', search='_search_user_dc', string='Related Users')
    salesperson_id = fields.Many2one('res.partner', 'Salesperson', domain=[('is_employee', '=', True)])
    warehouse_ids = fields.Many2many('stock.warehouse', string='Warehouses allowed access')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', copy=False)
    state = fields.Selection([('draft', 'draft'), ('validated', 'validated')], 'Status', default='draft')
    active = fields.Boolean('Active', help="The active field allows you to hide the category without removing it.", default= False)
    
    @api.multi
    def customer_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for change_state in self:
            change_state.active = True
            change_state.state = "validated"
    
    @api.model
    def create(self, values):
        res = []
        if values.get('dc_id') and values.get('this_for_all'):
            raise UserError(_("DC information must be empty when 'This for all' field checked !"))
        else:
            res = super(partner, self).create(values)
            res.CreateSettings()
            
        return res
    
    @api.multi
    def write(self, values):
        res = []
        #CHECKKK IF USER EDIT THE FIELD..IF USER NOT, THE "VALUES" WONT CONTAIN THE KEY OF THE FIELD SOO IT WILL RAISE KEYERROR WARNING
        #SOO IF USER NOT EDIT THE FIELD THAT USE FOR CONDITIONAL(DC_ID AND THIS_FOR_ALL), THOSE TWO FIELDS VALUE WILL SET FROM THE SELF. WHICH IS CONTAIN THE LATEST SAVED DATA
        for data_res in self:
            if 'dc_id' not in values.keys():
                values.update({'dc_id':data_res.dc_id.id}) 
            if 'this_for_all' not in values.keys():
                values.update({'this_for_all':data_res.this_for_all})
    
            if values.get('this_for_all') and values.get('dc_id'):
                raise UserError(_("DC information must be empty when 'This for all' field checked !"))
            else:
                res = super(partner, self).write(values)
                self.CreateSettings()
        return res

    @api.model
    def CreateSettings(self):
        for partner in self:
            if partner.this_for_all:
                if partner.is_consignment or partner.is_team_leader:
                    raise UserError (_("Main company can't as consignment or TL."))
            elif partner.is_dc:
                if not partner.ref:
                    raise UserError(_('Fill Internal Reference for DC first.(in Tab Sale & Purchases)'))

                if partner.warehouse_id:
                    return
                else:
                    wh_exist = self.env['stock.warehouse'].search(
                        ['|', ('name', '=', partner.name), ('code', '=', partner.ref or '-')])
                    if wh_exist:
                        partner.warehouse_id = wh_exist.id
                        return
                    wh_vals = {
                        'name': partner.name,
                        'code': partner.ref,
                        'dc_id': partner.id,
                        'partner_id': partner.id
                    }
                    new_wh = self.env['stock.warehouse'].create(wh_vals)
                    partner.warehouse_id = new_wh.id
                    if len(new_wh) == 0:
                        raise UserError(_("Ups, cannot create warehouse %s" % partner.name))

                ir_model_obj = self.pool['ir.model.data']
                type_obj = self.env['stock.picking.type']
                loc_obj = self.env['stock.location']
                seq_in = new_wh.in_type_id.sequence_id
                seq_out = new_wh.out_type_id.sequence_id
                view_location = new_wh.view_location_id
                stock_location = new_wh.lot_stock_id

                # RENAME VIEW LOCATION
                # for DC's warehouse, fill partner_id = dc_id
                view_location.write({
                    'name': partner.name,
                    'partner_id': partner.id,
                    'dc_id': partner.id
                })

                # update stock location, fill partner_id = dc_id
                stock_location.write({
                    'partner_id': partner.id,
                    'dc_id': partner.id
                })                

                # GET INFORMATION NDC
                model, ndc_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'stock', 'warehouse0')
                NDC = self.env['stock.warehouse'].search([('id','=',ndc_id)])
                NDC_Delivery = NDC.out_type_id

                model, customers_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'stock', 'stock_location_customers')
                model, ndc_transit_qua_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'pti_stock_default_mto', 'ndc_transit_quarantine')
                model, ndc_stag_loc_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'pti_stock_default_mto', 'ndc_staging')
                model, pick_tran_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'pti_stock_default_mto', 'picking_quarantine')
                model, ndc_quarantine_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'pti_stock_default_mto', 'ndc_quarantine')

                for l in ['Transit', 'Quarantine', 'Bad Products']:
                    loc = loc_obj.create({
                        'name' : l, 
                        'location_id': view_location.id, 
                        'usage': 'internal', 
                        'active': True,
                        'partner_id': partner.id,
                        'dc_id': partner.id
                    })
                    if l == 'Quarantine':
                        # CREATE OPERATION CUSTOMERS TO DISTRIBUTION CENTER
                        type_customer = type_obj.create({
                            'name' : 'Customers to %s' % (partner.name,),
                            'default_location_src_id': customers_id,
                            'default_location_dest_id': loc.id,
                            'sequence_id': seq_in.id,
                            'warehouse_id': new_wh.id,
                            'code' : 'internal'
                        })
                        new_wh.out_type_id.write({
                            'return_picking_type_id': type_customer.id
                        })
                        # CREATE OPERATION DC TO NDC
                        type_obj.create({
                            'name': '%s to NDC' % (partner.name,),
                            'default_location_src_id': loc.id,
                            'default_location_dest_id': ndc_transit_qua_id,
                            'sequence_id': seq_out.id,
                            'warehouse_id': new_wh.id,
                            'code' : 'internal'
                        })
                    if l == 'Transit':
                        # CREATE OPERATION TRANSIT FROM DISTRIBUTION CENTER
                        type_transit = type_obj.create({
                            'name': 'Receipts from %s' % (l,),
                            'default_location_src_id': loc.id,
                            'default_location_dest_id': stock_location.id,
                            'sequence_id': seq_in.id,
                            'warehouse_id': new_wh.id,
                            'code': 'internal',
                            'is_sjb_operation': True
                        })
                        new_wh.in_type_id.write({
                            'name': 'NDC to %s' % (partner.name,),
                            'code': 'internal',
                            'sequence_id': NDC_Delivery.sequence_id.id,
                            'warehouse_id': NDC.id,
                            'apply_mto': True,
                            'default_location_src_id': ndc_stag_loc_id,
                            'default_location_dest_id': loc.id
                        })
                        #add the 6th operation type
                        type_obj.create({
                            'name' : '%s to Other DC' % (partner.name,),
                            'default_location_src_id': stock_location.id,
                            'default_location_dest_id': stock_location.id,
                            'sequence_id': seq_out.id,
                            'warehouse_id': new_wh.id,
                            'code' : 'internal'
                        })

                        # PREPARE ROUTE AND PUSH RULES
                        routes = self.env['stock.location.route']
                        path = self.env['stock.location.path']
                        routes_id = routes.search([('name' ,'=', 'PTI ROUTES')], limit=1)
                        if len(routes_id) == 0:
                            res = routes.create({
                                'name': 'PTI ROUTES', 
                                'active': True,
                                'warehouse_selectable': True
                            })
                            path.create({
                                'route_id': res.id,
                                'name': 'transit to %s' % (partner.name,),
                                'location_from_id': loc.id,
                                'location_dest_id': stock_location.id,
                                'picking_type_id': type_transit.id,
                                'active': True
                            })
                            
                            partner.addWarehouse(res.id,new_wh.id)
                            partner.addWarehouse(res.id,NDC.id)
                        else:
                            exist = path.search([('location_from_id','=',loc.id),('location_dest_id','=',stock_location.id)])
                            if not exist.id:
                                path.create({
                                    'route_id': routes_id.id,
                                    'name': 'transit to %s' % (partner.name,),
                                    'location_from_id': loc.id,
                                    'location_dest_id': stock_location.id,
                                    'picking_type_id': type_transit.id,
                                    'active': True
                                })

                                partner.addWarehouse(routes_id.id,new_wh.id)
                
        return True
    
    @api.model
    def addWarehouse(self, route_id, wh_id):
        if not self.checkWHexist(route_id,wh_id):
            self.insertM2m(route_id,wh_id)
            
    @api.model
    def checkWHexist(self, route_id, wh_id): 
        if not route_id:
            return False
        self.env.cr.execute('''SELECT COUNT(*) 
                        FROM stock_route_warehouse 
                            WHERE route_id=%s and warehouse_id=%s''' ,(route_id,wh_id))  
        res = self.env.cr.fetchone()
        if len(res)==0:
            return False
        else:
            return True if res[0]==1 else False
        
    @api.model
    def insertM2m(self, route_id, wh_id):
        if not route_id:
            return False
        res = self.env.cr.execute('''INSERT INTO stock_route_warehouse (route_id,warehouse_id) 
                                    VALUES (%s, %s)''' ,(route_id,wh_id))
        return res 

    @api.model
    def UpdateSettings(self, values):
        '''
        @param values : dictionary will be use to update name warehouse and location
        for now not used yet
        '''
        wh_exist = self.env['stock.warehouse'].search(['|',('name','=',self.name),('code','=','DC' + self.ref or '-')])
        wh_exist.code = 'DC' + values['ref']
        location = self.env['stock.location'].search([('name', '=', self.ref)])
        if not location.id:
            raise UserError(_("Ups, Please contact Administrator."))
        location_2 = self.env['stock.location'].search([('name', '=', wh_exist.name), ('location_id', '=', location.id)])
        location_2.name = values['name']
        wh_exist.name = values['name']
        

class sale_order(models.Model):
    _inherit = "sale.order"
    
    @api.model
    def _get_defaultDC(self):
        return self.env.user.partner_id.dc_id

    @api.model
    def _get_pricelist_default(self):
        return self.env['product.pricelist'].search([('id', '=', 1)])
    
    _defaults = {
     'pricelist_id':_get_pricelist_default,
     }
        
    @api.one
    def _groups_access(self):
        allow = False
        hv_access = [
                     {'module' : 'pti_branch', 'group_id' : 'group_pti_branch_finance_admin'}
                    ]
        ir_model_data = self.env['ir.model.data']
        res = []
        testes = 0
        for data in hv_access:
            temp = ir_model_data.get_object_reference(data['module'], data['group_id'])[1]
            if temp:
                res.append(temp)
        user = self.env.user
        is_allowed_group_ids = tuple(res)

        for group in user.groups_id:
            if group.id in is_allowed_group_ids:
                allow = True
                break
        self.access_group = allow
        
    access_group = fields.Boolean(compute='_groups_access', string='Access groups', default=False)    
    dc_id = fields.Many2one('res.partner','Distribution Center',default=_get_defaultDC)
    sales_id = fields.Many2one('res.partner', string='Salesperson')
    
    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(sale_order, self)._prepare_invoice()
        top_partner = self.partner_id.property_payment_term_id.id
        if invoice_vals.get('payment_term_id'):
            if invoice_vals['payment_term_id'] != top_partner and top_partner != False:
                invoice_vals['payment_term_id'] = top_partner 
        else:
            invoice_vals['payment_term_id'] = top_partner or self.payment_term_id.id
        return invoice_vals


class warehouse(models.Model):
    _inherit = "stock.warehouse"
    
    dc_id = fields.Many2one('res.partner','Distribution Center')
    code = fields.Char('Short Name', size=12, required=True, help="Short name used to identify your warehouse")
    
class stockPickingType(models.Model):
    _inherit = "stock.picking.type"
    
    partner_operators = fields.Many2many('res.partner') # not used after implement is_sjb_operation
    is_sjb_operation = fields.Boolean(string='SJB operation', default=False)
    is_retur=fields.Boolean('Retur', default=False)

class location(models.Model):
    _inherit = "stock.location"
    
    dc_id = fields.Many2one('res.partner','Distribution Center')
    this_for_all = fields.Boolean('This location for all DC ?')


class journal(models.Model):
    _inherit = "account.journal"
    
    dc_id = fields.Many2one('res.partner','Distribution Center')
    this_for_all = fields.Boolean('This account for all DC ?')


class invoice(models.Model):
    _inherit = "account.invoice"
    
    sales_id = fields.Many2one('res.partner', string='Salesperson')

    @api.model
    def _get_defaultDC(self):
        return self.env.user.partner_id.dc_id or False
        
    @api.one
    def _groups_access(self):
        allow = False
        hv_access = [
                     {'module' : 'pti_branch', 'group_id' : 'group_pti_branch_finance_admin'}
                    ]
        ir_model_data = self.env['ir.model.data']
        res = []
        testes = 0
        for data in hv_access:
            temp = ir_model_data.get_object_reference(data['module'], data['group_id'])[1]
            if temp:
                res.append(temp)
        user = self.env.user
        is_allowed_group_ids = tuple(res)

        for group in user.groups_id:
            if group.id in is_allowed_group_ids:
                allow = True
                break
        self.access_group = allow
        
    access_group = fields.Boolean(compute='_groups_access', string='Access groups', default=False)    
    
    dc_id = fields.Many2one('res.partner','Distribution Center',default=_get_defaultDC)    
    
    @api.model
    def create(self, values):
        new_vals = values.copy()
        if 'origin' in values:
            sale_order = self.env['sale.order'].search([('name','=',values['origin'])])
            new_vals['sales_id'] = sale_order.sales_id.id
            if 'dc_id' not in new_vals:
                new_vals['dc_id'] = sale_order.dc_id.id
                if not new_vals['dc_id']:
                    inv = self.search([('number','=',values['origin'])],limit=1)
                    new_vals['dc_id'] = inv.dc_id.id
                if not new_vals['dc_id']:
                    vendor = False
                    if new_vals.get('partner_id'):
                        vendor = self.env['res.partner'].browse([new_vals['partner_id'] or False])
                        new_vals['dc_id'] = vendor.dc_id.id
                    if vendor and vendor.supplier:
                        next
        
        return super(invoice, self).create(new_vals)

