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
from docutils.nodes import Invisible
from openerp.osv.orm import setup_modifiers
from lxml import etree

class customerDiscount(models.Model):
    _name = "customer.discount"
    
    partner_id = fields.Many2one('res.partner', 'Customer')
    discount_id = fields.Many2one('discount.discount', 'Discount')
    
class areaarea(models.Model):
    _inherit = "area.area"
    
    partner_ids = fields.Many2many('res.partner', 'partner_area_rel', 'area_id', 'partner_id', string='Partner', copy=False)
    
class customers(models.Model):
    _inherit = "res.partner"
    
    npwp = fields.Char('NPWP')
    district = fields.Char('Kecamatan',help="Kecamatan")
    sub_district = fields.Char('Kelurahan',help="Kelurahan")
    npwp = fields.Char('NPWP')
    distribution_channel = fields.Many2one('distribution.channel', 'Distribution Channel')
    sub_distribution_channel = fields.Many2one('sub.distribution.channel', 'Sub Channel')
    outlet_type = fields.Many2one('outlet.outlet', 'Outlet Type')
    outlet_category = fields.Many2one('outlet.category', 'Outlet Category')
    discount_customer = fields.One2many('customer.discount', 'partner_id')
    payment_category = fields.Many2one('payment.category', 'Payment method')
    area = fields.Many2many('area.area', 'partner_area_rel', 'partner_id', 'area_id', string='Area', copy=False)
    tax_address = fields.Char('Tax Address')
    tax_name = fields.Char('Tax Name')
    is_consignment = fields.Boolean('Consignment')
    is_team_leader = fields.Boolean('TL')
    customer_groups = fields.Many2one('partner.group','Customers Group')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', copy=False)
    
    _defaults = {
        'company_type': 'company'
    }
    
    @api.model
    def create(self, values):
        res = super(customers, self).create(values)
        res.CreateConsigmentSettings({'create' : True})
        return res
    
    @api.multi
    def write(self, values):
        res = super(customers, self).write(values)
        self.CreateConsigmentSettings(values)
        return res
    
    def CreateConsigmentSettings(self, values):
        for partner in self:
            CODE = 'C'
            query = "select id from stock_warehouse order by id desc limit 1"
            if partner.is_consignment and partner.is_dc:
                raise UserError(_("Ups, Customer can't be Consignment and Distribution center")) 
            if partner.is_consignment or partner.is_team_leader:
                if not partner.dc_id.id and not partner.this_for_all:
                    raise UserError(_('Fill DC Information please'))
                if not partner.ref:
                    raise UserError(_('Fill internal reference Information.'))
                if partner.is_team_leader:
                    CODE = partner.ref

                self.env.cr.execute(query)
                data = self.env.cr.fetchone()
                if len(data) == 0:
                    raise UserError(_("Ups, cannot retrieve warehouse data. Please contact Administrator."))
                # if partner_id filled in wh_vals, it will raise procurement exception
                dc_id = partner.dc_id.id
                if partner.warehouse_id:
                    return
                else:
                    wh_exist = self.env['stock.warehouse'].search([('name','=',partner.name),('dc_id','=',partner.dc_id.id)], limit=1)
                    if wh_exist.id:
                        partner.warehouse_id = wh_exist.id
                        return
                    if partner.is_consignment:
                        CODE = 'C%s' % data[0]
                        wh_vals = {
                            'name' : partner.name,
                            'code' : CODE,
                            'dc_id' : dc_id
                        }
                    if partner.is_team_leader:
                        CODE = 'MW%s' % data[0]
                        wh_vals = {
                            'name' : partner.name,
                            'code' : CODE,
                            'dc_id' : dc_id
                        }
                    new_wh = self.env['stock.warehouse'].create(wh_vals)
                    partner.warehouse_id = new_wh.id

                # UPDATE DC AND OWNER OF VIEW LOCATION IN THE NEW WAREHOUSE
                location_view = new_wh.view_location_id
                if not location_view.id:
                    raise UserError(_("Ups, no view location in warehouse '%s'. Please contact Administrator." % (self.name)))
                location_view.update({
                    'partner_id': partner.id,
                    'dc_id': dc_id,
                    'name': CODE
                })
                
                # SEARCH LOCATION NEW WAREHOUSE UPDATE DC, OWNER AND NAME
                location_stock = new_wh.lot_stock_id
                if not location_stock.id:
                    raise UserError(_("Ups, no stock location in warehouse '%s'. Please contact Administrator." % (self.name)))
                location_stock.update({
                    'partner_id': partner.id,
                    'dc_id': dc_id
                })
                
                # SEARCH DC LOCATION
                # DC location criteria : dc_id = partner_id
                # Consignment location : dc_id != partner_id (partner_id = NULL)
                # Mobile WH : dc_id != partner_id (partner_id = NULL)
                warehouse_dc = self.env['stock.warehouse'].search([('dc_id','=',dc_id),('partner_id','=',dc_id)], limit=1)
                if not warehouse_dc.id:
                    raise UserError(_("Ups, there is no '%s' warehouse. Please contact Administrator." % (partner.dc_id.name)))

                new_wh.int_type_id.write({
                    'name': '%s to %s' % (partner.dc_id.name, partner.name),
                    'default_location_src_id': warehouse_dc.lot_stock_id.id,
                    'sequence_id': warehouse_dc.out_type_id.sequence_id.id,
                })

        return True

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(customers, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        xpath_field = "//field[@name='ref']"
        doc = etree.XML(res['arch'])
        for node in doc.xpath(xpath_field):
            if self._context.get('search_default_customer') == 1:
                node.set('string', "Customer Code")
            if self._context.get('search_default_supplier') == 1:
                node.set('string', "Vendor Code")
            setup_modifiers(node, res['fields']['ref'])
            res['arch'] = etree.tostring(doc)
        return res

customers()

