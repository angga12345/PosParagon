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

import time
import logging
import base64
import xlwt
from xlwt import *
import cStringIO
import xlsxwriter
from cStringIO import StringIO
import base64
import tempfile
import os
from openerp.osv import fields, osv
from xlsxwriter.workbook import Workbook
from openerp.tools.translate import _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from datetime import datetime
import pytz
from xlsxwriter.utility import xl_rowcol_to_cell
_logger = logging.getLogger(__name__)

class stock_card(osv.osv_memory):
     
    _name = "stock.card"
        
    _columns = {
        'data_x': fields.binary('File', readonly=True),  
        'name': fields.char('Filename', 100, readonly=True),
        'product_ids' : fields.many2one('product.product','Product'), 
        'date_from'    : fields.date('Date From'),
        'date_to'    : fields.date('Date To'),
        'state_x': fields.selection( ( ('choose','choose'),('get','get'),)), #xls
    }
    
    _defaults = {
        'state_x': lambda *a: 'choose',
    }

    def ctx_excel_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['form'] = self.read(cr, uid, ids, ['date_from','date_to','product_ids'], context=context)[0]
        return self._excel_report(cr, uid, ids, data, context=context)
            
    def _excel_report(self, cr, uid, ids, data, context=None):
        move_obj = self.pool.get('stock.move')
        report_obj = self.browse(cr, uid, ids, context=context)
        
        fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        filename = 'stockcard_report.xlsx'
        
        bold = workbook.add_format({'bold': 1})
        bold_header = workbook.add_format({'bold': 1})
        bold_header.set_font_size('16')
        bold_center = workbook.add_format({'bold': 1,'align': 'center','border':1,'valign':'vcenter'})
        bold_center.set_text_wrap()
        bold_center.set_bg_color('#BDC3C7')
        date_center = workbook.add_format({'border':1,'align': 'left','num_format': 'dd-MMM-yyyy'})
        bgcolor = workbook.add_format({'bold': 1})
        bgcolor.set_bg_color('#FFFF99')
        bgcolor.set_border()
        content_table = workbook.add_format({'border': 1})
        content_table.set_text_wrap()
        
        worksheet = workbook.add_worksheet("Daily Stock Report")
        worksheet.set_paper(9)
        worksheet.set_landscape()
        worksheet.set_margins(0.5, 0.3, 0.5, 0.5)
        worksheet.freeze_panes(5,0)
        worksheet.set_column('A:A', 12)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 27)
        worksheet.set_column('D:D', 8)
        worksheet.set_column('E:G', 9)  
        
        worksheet.merge_range('A1:K1','Stock Card Report', bold_header)
        worksheet.merge_range('A2:K2', 'Period : ' + str(date_from) + ' - ' + str(date_to),bold)
        moves = move_obj.search(cr, uid, [('product_id.id','=', report_obj.product_ids.id),('state','=','done'),('date','>=',date_from),
                                          ('date','<=',date_to)], order='date ASC')
        
        moves2 = move_obj.search(cr, uid, [('product_id.id','=', report_obj.product_ids.id),('state','=','done'),('date','<',date_from)], order='date ASC')
        
        
        quantity=0  
        for data in move_obj.browse(cr,uid,moves2,context): 
            if data.transaction_desc == 'Receive' or data.transaction_desc == 'Receive2':
                quantity += data.product_uom_qty
            elif data.transaction_desc == 'Consume':
                quantity -= data.product_uom_qty
                    
        worksheet.merge_range('A3:K3', 'Product : [' + report_obj.product_ids.default_code + '] ' + report_obj.product_ids.product_tmpl_id.name, bold)
       
        row = 1             
        worksheet.write(row+3,0,'Date', bold_center)        
        worksheet.write(row+3,1,'No Ref', bold_center)
        worksheet.write(row+3,2,'Description', bold_center)
        worksheet.write(row+3,3,'Project Code', bold_center)
        worksheet.write(row+3,4,'PO Number', bold_center)
        worksheet.write(row+3,5,'MRC Number', bold_center)
        worksheet.write(row+3,6,'NIK Number', bold_center)
        worksheet.write(row+3,7,'Incoming', bold_center)
        worksheet.write(row+3,8,'Outgoing', bold_center)
        worksheet.write(row+3,9,'Reverse', bold_center)
        worksheet.write(row+3,10,'Balance', bold_center)
        date_time = datetime.strptime(date_from, "%Y-%m-%d")
        worksheet.write(row+4,0, date_time, date_center)  
        worksheet.write(row+4,1,'Opening Balance', content_table)
        worksheet.merge_range('C6:J6','',content_table)
        worksheet.write(row+4,10, quantity,content_table)
              
        row+=4
        qty_in=0
        qty_out=0
        totalin = 0
        totalout = 0
        totalrev = 0

        for data in move_obj.browse(cr, uid, moves, context=context):
            if data.transaction_desc == 'Receive':
                name = data.picking_id.name
                partner = data.picking_id.partner_id.name
                date = data.date
                date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                date = datetime.strftime(date, "%Y-%m-%d")
                date = datetime.strptime(date, "%Y-%m-%d")
                desc = data.transaction_desc
                prn = data.prn_id.name
                po = data.picking_id.origin
                qty_in = data.product_uom_qty
                qty_in_factor = data.product_id.uom_po_id.factor_inv*qty_in
                qty_out=0
                qty_reverse=0
                quantity=quantity+qty_in_factor
                totalin=totalin+qty_in
                
                if not partner:
                    partnerNew = data.location_id.name
                else:
                    partnerNew = partner
                    
                descNew = desc+" from "+partnerNew
                
                worksheet.write(row+1,0,date,date_center)
                worksheet.write(row+1,1,name or '',content_table)
                worksheet.write(row+1,2,descNew,content_table)
                worksheet.write(row+1,3,prn or '',content_table)
                worksheet.write(row+1,4,po or '',content_table)
                worksheet.write(row+1,5,data.mrc_number or '',content_table)
                worksheet.write(row+1,6,data.nik_number or '',content_table)
                worksheet.write(row+1,7,qty_in,content_table)
                worksheet.write(row+1,8,qty_out,content_table)
                worksheet.write(row+1,9,qty_reverse,content_table)
                worksheet.write(row+1,10,quantity,content_table)
                row+=1 
            
            elif data.transaction_desc == 'Receive2':
                name = data.picking_id.name
                partner = data.picking_id.partner_id.name
                date = data.date
                date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                date = datetime.strftime(date, "%Y-%m-%d")
                date = datetime.strptime(date, "%Y-%m-%d")
                desc = 'Receive from ' + data.location_id.name
                prn = data.prn_id.name
                po = data.picking_id.origin
                qty_in=0
                qty_out=0
                qty_reverse=0
                quantity=quantity+data.product_uom_qty
                                        
                worksheet.write(row+1,0,date,date_center)
                worksheet.write(row+1,1,name or '',content_table)
                worksheet.write(row+1,2,desc,content_table)
                worksheet.write(row+1,3,prn or '',content_table)
                worksheet.write(row+1,4,po or '',content_table)
                worksheet.write(row+1,5,data.mrc_number or '',content_table)
                worksheet.write(row+1,6,data.nik_number or '',content_table)
                worksheet.write(row+1,7,qty_in,content_table)
                worksheet.write(row+1,8,qty_out,content_table)
                worksheet.write(row+1,9,qty_reverse,content_table)
                worksheet.write(row+1,10,quantity,content_table)
                row+=1   
                
            elif data.transaction_desc == 'Consume' :            
                name = data.picking_id.name
                date = data.date
                date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                date = datetime.strftime(date, "%Y-%m-%d")
                date = datetime.strptime(date, "%Y-%m-%d")
                desc = data.transaction_desc
                prn = data.prn_id.name
                po = data.picking_id.origin
                qty_in=0      
                qty_out = data.product_uom_qty
                qty_reverse=0 
                quantity=quantity-qty_out   
                totalout=totalout+qty_out
                
                worksheet.write(row+1,0,date,date_center)
                worksheet.write(row+1,1,name or '',content_table)
                worksheet.write(row+1,2,desc,content_table)
                worksheet.write(row+1,3,prn or '',content_table)
                worksheet.write(row+1,4,po or '',content_table)
                worksheet.write(row+1,5,data.mrc_number or '',content_table)
                worksheet.write(row+1,6,data.nik_number or '',content_table)
                worksheet.write(row+1,7,qty_in,content_table)
                worksheet.write(row+1,8,qty_out,content_table)
                worksheet.write(row+1,9,qty_reverse,content_table)
                worksheet.write(row+1,10,quantity,content_table)
                row+=1    
                
            elif data.transaction_desc == 'Reverse' :     
                name = data.picking_id.name
                date = data.date
                date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                date = datetime.strftime(date, "%Y-%m-%d")
                date = datetime.strptime(date, "%Y-%m-%d")
                desc = data.transaction_desc + ' from ' + data.location_id.name + ' to ' + data.location_dest_id.name
                prn = data.prn_id.name
                po = data.picking_id.origin
                qty_in=0
                qty_out=0   
                qty_reverse = data.product_uom_qty
                totalrev += qty_reverse
                quantity += qty_reverse
                
                worksheet.write(row+1,0,date,date_center)
                worksheet.write(row+1,1,name or '',content_table)
                worksheet.write(row+1,2,desc,content_table)
                worksheet.write(row+1,3,prn or '',content_table)
                worksheet.write(row+1,4,po or '',content_table)
                worksheet.write(row+1,5,data.mrc_number or '',content_table)
                worksheet.write(row+1,6,data.nik_number or '',content_table)
                worksheet.write(row+1,7,qty_in,content_table)
                worksheet.write(row+1,8,qty_out,content_table)
                worksheet.write(row+1,9,qty_reverse,content_table)
                worksheet.write(row+1,10,quantity,content_table)
                row+=1  
                
#             elif data.transaction_desc == 'Reverse2' :     
#                 name = data.picking_id.name
#                 date = data.date
#                 date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
#                 date = datetime.strftime(date, "%Y-%m-%d")
#                 date = datetime.strptime(date, "%Y-%m-%d")
#                 desc = 'Reverse from ' + data.location_id.name + ' to ' + data.location_dest_id.name
#                 prn = data.prn_id.name
#                 po = data.picking_id.origin
#                 qty_in=0
#                 qty_out=0   
#                 qty_reverse = data.product_uom_qty
#                 totalrev += qty_reverse
#                 quantity += qty_reverse
#                 
#                 worksheet.write(row+1,0,date,date_center)
#                 worksheet.write(row+1,1,name or '',content_table)
#                 worksheet.write(row+1,2,desc,content_table)
#                 worksheet.write(row+1,3,prn or '',content_table)
#                 worksheet.write(row+1,4,po or '',content_table)
#                 worksheet.write(row+1,5,data.mrc_number or '',content_table)
#                 worksheet.write(row+1,6,data.nik_number or '',content_table)
#                 worksheet.write(row+1,7,qty_in,content_table)
#                 worksheet.write(row+1,8,qty_out,content_table)
#                 worksheet.write(row+1,9,qty_reverse,content_table)
#                 worksheet.write(row+1,10,quantity,content_table)
#                 row+=1  
                
            elif data.transaction_desc == 'Reverse_Out' :            
                name = data.picking_id.name
                date = data.date
                date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                date = datetime.strftime(date, "%Y-%m-%d")
                date = datetime.strptime(date, "%Y-%m-%d")
                partner = data.picking_id.partner_id.name
                if not partner:
                    partnerNew = data.location_id.name
                else:
                    partnerNew = partner
                desc = 'Reverse to ' + partnerNew
                prn = data.prn_id.name
                po = data.picking_id.origin
                qty_in=0      
                qty_out = data.product_uom_qty
                qty_reverse=0 
                quantity=quantity-qty_out   
                totalout=totalout+qty_out
                
                worksheet.write(row+1,0,date,date_center)
                worksheet.write(row+1,1,name or '',content_table)
                worksheet.write(row+1,2,desc,content_table)
                worksheet.write(row+1,3,prn or '',content_table)
                worksheet.write(row+1,4,po or '',content_table)
                worksheet.write(row+1,5,data.mrc_number or '',content_table)
                worksheet.write(row+1,6,data.nik_number or '',content_table)
                worksheet.write(row+1,7,qty_in,content_table)
                worksheet.write(row+1,8,qty_out,content_table)
                worksheet.write(row+1,9,qty_reverse,content_table)
                worksheet.write(row+1,10,quantity,content_table)
                row+=1    
                
            elif data.transaction_desc == 'Reverse_Out2':
                name = data.picking_id.name
                partner = data.picking_id.partner_id.name
                date = data.date
                date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                date = datetime.strftime(date, "%Y-%m-%d")
                date = datetime.strptime(date, "%Y-%m-%d")
                desc = 'Send to ' + data.location_dest_id.name + ' (Adjustment)'
                prn = data.prn_id.name
                po = data.picking_id.origin
                qty_in=0
                qty_out=0
                qty_reverse=0
                quantity=quantity-data.product_uom_qty
                                        
                worksheet.write(row+1,0,date,date_center)
                worksheet.write(row+1,1,name or '',content_table)
                worksheet.write(row+1,2,desc,content_table)
                worksheet.write(row+1,3,prn or '',content_table)
                worksheet.write(row+1,4,po or '',content_table)
                worksheet.write(row+1,5,data.mrc_number or '',content_table)
                worksheet.write(row+1,6,data.nik_number or '',content_table)
                worksheet.write(row+1,7,qty_in,content_table)
                worksheet.write(row+1,8,qty_out,content_table)
                worksheet.write(row+1,9,qty_reverse,content_table)
                worksheet.write(row+1,10,quantity,content_table)
                row+=1 
                        
        worksheet.write(row+1,7, totalin, bgcolor)
        worksheet.write(row+1,8, totalout-totalrev, bgcolor)
        worksheet.write(row+1,9, totalrev, bgcolor)
        workbook.close()
        out=base64.encodestring(fp.getvalue())
        self.write(cr, uid, ids, {'state_x':'get', 'data_x':out, 'name': filename}, context=context)
        ir_model_data = self.pool.get('ir.model.data')
        fp.close()

        form_res = ir_model_data.get_object_reference(cr, uid, 'pti_stock_report', 'print_timber_report_view')

        form_id = form_res and form_res[1] or False
        return {
            'name': _('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.card',
            'res_id': ids[0],
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }
stock_card()
  