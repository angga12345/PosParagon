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

class date_consolidate_product(models.TransientModel):
    _name = 'date.consolidate.product'
    
    picking = fields.One2many(store=True,
        comodel_name='date.consolidate.product.line',
        inverse_name='consolidate_id',
        string='List of picking associated to this wave',
        compute='compute_qty'
        )
    name = fields.Char('Name', default='Product consolidate')
    date_consolidate = fields.Date('Start Date', required=True, default=lambda self: fields.datetime.now())
    consolidate_id = fields.Many2one('stock.picking', 'Consolidate Product')
    brand_consolidate=fields.Many2one('product.brand','Brand', required=True)

    @api.multi
    def create_consolidate_product(self):
        data = {}
        data['start_date'] = self.date_consolidate
        data['brand_cons'] = self.brand_consolidate
        return self._print_consolidate_product_report(data)
    
    @api.multi
    def _print_consolidate_product_report(self, data):
        serial_number = self.env['stock.picking'].search([
                                            ('min_date','>=',data['start_date'])])
            
        tempList=[]
        for report in serial_number:
            for pack_op in report.move_lines:
                if pack_op.product_id.tags.id == data['brand_cons'].id:
                    tempList.append({'id': pack_op.product_id.id,
                            'name': pack_op.product_id.name,
                            'qty': pack_op.product_uom_qty})
                
        temp = {v['id']:v for v in tempList}.values()
        picking_id = []
          
          
        for x in temp:
            jml=0
            for y in tempList:  
                if x.get('id')==y.get('id'):
                    jml+= y.get('qty')
                      
                          
            picking_id.append((0, 0,{'consolidate_id': self.id, 
                          'product_id': x.get('id'), 
                          'tot_qty': jml}))
              
        self.picking = picking_id                    
        
        return {
            'res_id': self.id,
            'name': 'date.consolidate.product.form',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'date.consolidate.product',
            'type': 'ir.actions.act_window',

        }
        
class date_consolidate_product_line(models.TransientModel):
    _name = "date.consolidate.product.line"
    
    consolidate_id = fields.Many2one(  
        comodel_name='date.consolidate.product',
        string='Consolidate Picking'
                                )
    tot_qty = fields.Float(string="Total QTY")
    product_id = fields.Many2one("product.product","Product")

