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
import logging
import time
from datetime import datetime, timedelta
from openerp import models, fields, api, _
from openerp.exceptions import UserError
import re
import base64
import cStringIO
import xlsxwriter
from cStringIO import StringIO
from gdata.calendar import UID
from openerp.exceptions import except_orm

_logger = logging.getLogger(__name__)

class deliver_report(models.TransientModel):
    _name = "do.report"
    
    start_date = fields.Date('Start date')
    end_date = fields.Date('End date')
    dc_id = fields.Many2one('res.partner', 'DC')
    company = fields.Selection([('all','All Company'),('paragon','Paragon'),('parama','Parama')])
    type = fields.Selection([('all','All Move'),('in','Move In'),('out','Move Out')])
    state_x = fields.Selection([('choose','choose'),('get','get')])
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    
    @api.model
    def _get_dc_default(self):
        uid = self._uid
        dc = False
        user_ids = self.env['res.users'].search([('id', '=', int(uid))])
        if user_ids:
            dc = user_ids[0].partner_id.dc_id.id or False
        return dc
    
    _defaults = {
        'state_x': lambda *a: 'choose',
        'company': lambda *a: 'all',
        'type': lambda *a: 'all',
        'dc_id': _get_dc_default
    }
    
    number_format = False
    bold_with_border = False
    
    @api.model
    def set_width(self, worksheet):
        worksheet.set_column('A1:A1', 20)
        worksheet.set_column('B1:B1', 30)
        worksheet.set_column('C1:C1', 50)
        worksheet.set_column('D1:D1', 10)
        return worksheet
        
    @api.model
    def add_workbook_format(self, workbook):
        self.bold_with_border = workbook.add_format({})
        self.bold_with_border.set_border()
        
        self.number_format = workbook.add_format({'align': 'right','num_format': '#,##0.00'})
        self.number_format.set_border()
        return workbook

    @api.multi
    def create_do_report(self):
        data = {}
        data['start_date'] = self.start_date
        data['end_date'] = self.end_date 
        data['company'] = self.company 
        return self._print_do_report_general(data)

    @api.multi
    def _print_do_report_general(self, data):
        company = ''
        if self.company == 'all':
            company = 'Paragon & Parama'
        elif self.company == 'paragon':
            company = 'Paragon'
        elif self.company == 'parama':
            company = 'Parama'
        filename = 'delivery_order_'+ company + '_' + self.type + '_report.xlsx'
        fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)
        workbook = self.add_workbook_format(workbook)
        picking_ids = {}

        ir_model_data = self.env['ir.model.data']
        finance_id = ir_model_data.get_object_reference('pti_branch', 'group_pti_branch_finance_admin')[1]

        is_finance = False
        for group in self.env.user.groups_id:
            if group.id == finance_id:
                is_finance = True
                break

        if is_finance:
            pick_type_ids = {}
            if self.dc_id:
                dc_name = self.dc_id.name
                warehouse_ids = self.env['stock.warehouse'].search([('name','=',dc_name)])
                pick_type_ids = self.env['stock.picking.type'].search([('warehouse_id','=',warehouse_ids[0].id)])
            pick_ids = []
            for out in pick_type_ids:
                pick_ids.append(out.id)
            if self.company == 'all':
                if self.type == 'all':
                    types = 'customer'
                    if self.dc_id:
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('state','=','done'),
                                                                    ('picking_type_id','in',pick_ids),'|',
                                                                    ('location_id.usage','=', types),
                                                                    ('location_dest_id.usage','=',types)
                                                                   ])
                    else:
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('state','=','done'),'|',
                                                                    ('location_id.usage','=', types),
                                                                    ('location_dest_id.usage','=',types)
                                                                   ])
                elif self.type == 'in':
                    types = 'customer'
                    if self.dc_id:
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('location_id.usage','=',types),
                                                                    ('state','=','done'),
                                                                    ('picking_type_id','in',pick_ids)
                                                                   ])
                    else:
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('location_id.usage','=',types),
                                                                    ('state','=','done')
                                                                   ])
                elif self.type == 'out':
                    types = 'customer'
                    if self.dc_id:
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('location_dest_id.usage','=',types),
                                                                    ('state','=','done'),
                                                                    ('picking_type_id','in',pick_ids)
                                                                   ])
                    else:
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('location_dest_id.usage','=',types),
                                                                    ('state','=','done')
                                                                   ])
            elif self.company == 'paragon':
                if self.type == 'all':
                    types = 'customer'
                    if self.dc_id:
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('name','not like','PRM'),
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('state','=','done'),
                                                                    ('picking_type_id','in',pick_ids),'|',
                                                                    ('location_id.usage','=', types),
                                                                    ('location_dest_id.usage','=',types)
                                                                   ])
                    else:
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('name','not like','PRM'),
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('state','=','done'),'|',
                                                                    ('location_id.usage','=', types),
                                                                    ('location_dest_id.usage','=',types)
                                                                   ])
                elif self.type == 'in':
                    types = 'customer'
                    if self.dc_id:
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('name','not like','PRM'),
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('location_id.usage','=',types),
                                                                    ('state','=','done'),
                                                                    ('picking_type_id','in',pick_ids)
                                                                   ])
                    else:
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('name','not like','PRM'),
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('location_id.usage','=',types),
                                                                    ('state','=','done')
                                                                   ])
                elif self.type == 'out':
                    types = 'customer'
                    if self.dc_id:
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('name','not like','PRM'),
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('location_dest_id.usage','=',types),
                                                                    ('state','=','done'),
                                                                    ('picking_type_id','in',pick_ids)
                                                                   ])
                    else:
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('name','not like','PRM'),
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('location_dest_id.usage','=',types),
                                                                    ('state','=','done')
                                                                   ])
                    
            elif self.company == 'parama':
                if self.type == 'all':
                    types = 'customer'
                    if self.dc_id:
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('name','like','PRM'),
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('state','=','done'),
                                                                    ('picking_type_id','in',pick_ids),'|',
                                                                    ('location_id.usage','=', types),
                                                                    ('location_dest_id.usage','=',types)
                                                                   ])
                    else:
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('name','like','PRM'),
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('state','=','done'),'|',
                                                                    ('location_id.usage','=', types),
                                                                    ('location_dest_id.usage','=',types)
                                                                   ])
                elif self.type == 'in':
                    types = 'customer'
                    if self.dc_id:
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('name','like','PRM'),
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('location_id.usage','=',types),
                                                                    ('state','=','done'),
                                                                    ('picking_type_id','in',pick_ids)
                                                                   ])
                    else:
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('name','like','PRM'),
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('location_id.usage','=',types),
                                                                    ('state','=','done')
                                                                   ])
                elif self.type == 'out':
                    types = 'customer'
                    if self.dc_id:
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('name','like','PRM'),
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('location_dest_id.usage','=',types),
                                                                    ('state','=','done'),
                                                                    ('picking_type_id','in',pick_ids)
                                                                   ])
                    else:
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('name','like','PRM'),
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('location_dest_id.usage','=',types),
                                                                    ('state','=','done')
                                                                   ])
                
        else:
            if self.dc_id:
                dc_name = self.dc_id.name
                warehouse_ids = self.env['stock.warehouse'].search([('name','=',dc_name)])
                pick_type_ids = self.env['stock.picking.type'].search([('warehouse_id','=',warehouse_ids[0].id)])
                pick_ids = []
                for out in pick_type_ids:
                    pick_ids.append(out.id)
                if self.company == 'all':
                    if self.type == 'all':
                        types = 'customer'
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('state','=','done'),
                                                                    ('picking_type_id','in',pick_ids),'|',
                                                                    ('location_id.usage','=', types),
                                                                    ('location_dest_id.usage','=',types)
                                                                   ])
                    elif self.type == 'in':
                        types = 'customer'
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('state','=','done'),
                                                                    ('location_id.usage','=',types),
                                                                    ('picking_type_id','in',pick_ids)
                                                                   ])
                    elif self.type == 'out':
                        types = 'customer'
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('state','=','done'),
                                                                    ('location_dest_id.usage','=',types),
                                                                    ('picking_type_id','in',pick_ids)
                                                                   ])
                elif self.company == 'paragon':
                    if self.type == 'all':
                        types = 'customer'
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('name','not like','PRM'),
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('state','=','done'),
                                                                    ('picking_type_id','in',pick_ids),'|',
                                                                    ('location_id.usage','=', types),
                                                                    ('location_dest_id.usage','=',types)
                                                                   ])
                    elif self.type == 'in':
                        types = 'customer'
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('name','not like','PRM'),
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('state','=','done'),
                                                                    ('location_id.usage','=',types),
                                                                    ('picking_type_id','in',pick_ids)
                                                                   ])
                    elif self.type == 'out':
                        types = 'customer'
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('name','not like','PRM'),
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('state','=','done'),
                                                                    ('location_dest_id.usage','=',types),
                                                                    ('picking_type_id','in',pick_ids)
                                                                   ])
                elif self.company == 'parama':
                    if self.type == 'all':
                        types = 'customer'
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('name','like','PRM'),
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('state','=','done'),
                                                                    ('picking_type_id','in',pick_ids),'|',
                                                                    ('location_id.usage','=', types),
                                                                    ('location_dest_id.usage','=',types)
                                                                   ])
                    elif self.type == 'in':
                        types = 'customer'
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('name','like','PRM'),
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('state','=','done'),
                                                                    ('location_id.usage','=',types),
                                                                    ('picking_type_id','in',pick_ids)
                                                                   ])
                    elif self.type == 'out':
                        types = 'customer'
                        picking_ids = self.env['stock.picking'].search([
                                                                    ('name','like','PRM'),
                                                                    ('date_done','>=',data['start_date']),
                                                                    ('date_done','<=',data['end_date']),
                                                                    ('state','=','done'),
                                                                    ('location_dest_id.usage','=',types),
                                                                    ('picking_type_id','in',pick_ids)
                                                                   ])
            else:
                raise except_orm(_('Warning!'),_('Please set distribution center for your user'))

        worksheet = workbook.add_worksheet("Delivery Order Report")
        worksheet.hide_gridlines(1)
        worksheet = self.set_width(worksheet)

        worksheet.write(0, 0, "Report Name :", self.bold_with_border)
        worksheet.write(1, 0, "Interval From :", self.bold_with_border)
        worksheet.write(2, 0, "Interval To :", self.bold_with_border)
        worksheet.write('B1', 'Delivery Order ' +company, self.bold_with_border)
        worksheet.write('B2', data['start_date'], self.bold_with_border)
        worksheet.write('B3', data['end_date'], self.bold_with_border)
        
        worksheet.write(4, 0, "Picking Number", self.bold_with_border)
        worksheet.write(4, 1, "DC", self.bold_with_border)
        worksheet.write(4, 2, "Product Name", self.bold_with_border)
        worksheet.write(4, 3, "Total QTY", self.bold_with_border)
        
        baris = 5
        nomor = 0
        
        if self.company == 'parama':
            for data in picking_ids:
                if data.name[0:4] == 'PRM/':
                    worksheet.write(baris, 0, data.name , self.bold_with_border)
                    worksheet.write(baris, 1, data.picking_type_id.warehouse_id.name , self.bold_with_border)
                    lenght = len(data.pack_operation_product_ids)
                    check = 0
                    for line in data.pack_operation_product_ids:
                        check += 1
                        worksheet.write(baris, 2, line.product_id.name , self.bold_with_border)
                        worksheet.write(baris, 3, line.qty_done , self.number_format)
                        if lenght > 1 and check < lenght:
                            baris = baris + 1
                            nomor = nomor + 1
                    baris = baris + 1
                    nomor = nomor + 1
        else:
            for data in picking_ids:
                worksheet.write(baris, 0, data.name , self.bold_with_border)
                worksheet.write(baris, 1, data.picking_type_id.warehouse_id.name , self.bold_with_border)
                lenght = len(data.pack_operation_product_ids)
                check = 0
                for line in data.pack_operation_product_ids:
                    check += 1
                    worksheet.write(baris, 2, line.product_id.name , self.bold_with_border)
                    worksheet.write(baris, 3, line.qty_done , self.number_format)
                    if lenght > 1 and check < lenght:
                        baris = baris + 1
                        nomor = nomor + 1
                baris = baris + 1
                nomor = nomor + 1
            
        workbook.close()
        out=base64.encodestring(fp.getvalue())
        self.write({'state_x':'get', 'data_x':out, 'name': filename})

        ir_model_data = self.pool.get('ir.model.data')
        fp.close()
        form_res = ir_model_data.get_object_reference(self._cr, self._uid, 'do_report', 'deliver_report_form')
        form_id = form_res and form_res[1] or False
        return {
            'name': _('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'do.report',
            'res_id': self.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

