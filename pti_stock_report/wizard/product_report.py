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
# for reserved_qty
from openerp.tools.float_utils import float_compare, float_round 
from openerp.exceptions import UserError

_logger = logging.getLogger(__name__)

class product_report(osv.osv_memory):
     
    _name = "qoh.product.report"
        
    _columns = {
        'partner_id' : fields.many2one('res.partner', 'Owner'),        
        'data_x': fields.binary('File', readonly=True),
        'name': fields.char('Filename', 100, readonly=True),
        'location_id' : fields.many2one('stock.location','Location'), 
        'state_x': fields.selection( ( ('choose','choose'),('get','get'),)), #xls
    }
    
    _defaults = {
        'state_x': lambda *a: 'choose',
    }
    
    def qoh_excel_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['form'] = self.read(cr, uid, ids, ['location_id'], context=context)[0]
        return self._excel_report(cr, uid, ids, data, context=context)
    
    def _get_reserved_move(self, cr, uid, ids, context=None):
        uom_obj = self.pool.get('product.uom')
        res = dict.fromkeys(ids, '')
        precision = self.pool['decimal.precision'].precision_get(cr, uid, 'Product Unit of Measure')
        for move in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
            if move.state in ('draft', 'done', 'cancel') or move.location_id.usage != 'internal':
                res[move.id] = ''  # 'not applicable' or 'n/a' could work too
                continue
            total_available = min(move.product_qty, move.reserved_availability + move.availability)
            total_available = uom_obj._compute_qty_obj(cr, uid, move.product_uom, total_available, move.product_id.uom_id, round=False, context=context)
            total_available = float_round(total_available, precision_digits=precision)
            reserved = 0
            if move.reserved_availability:
                if move.reserved_availability != total_available:
                    #some of the available quantity is assigned and some are available but not reserved
                    reserved_available = uom_obj._compute_qty_obj(cr, uid, move.product_uom, move.reserved_availability, move.product_id.uom_id, round=False, context=context)
                    reserved = reserved_available
                else:
                    #all available quantity is assigned
                    reserved = total_available
            res[move.id] = reserved
        return res
     
    def _excel_report(self, cr, uid, ids, data, context=None):
        product_obj = self.pool.get('product.product')
        report_obj = self.browse(cr, uid, ids, context=context)
        location_id = data['form']['location_id']
        fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)
        filename = 'QoH_Product_Report.xlsx'
        
        bold = workbook.add_format({'bold': 1})
        bold.set_font_size('14')
        bold2 = workbook.add_format({'bold': 1})
        bold2.set_font_size('12')
        bold_center = workbook.add_format({'bold': 1,'align': 'center','border':1,'valign':'vcenter'})
        bold_center.set_text_wrap()
        bold_center.set_bg_color('#D3D3D3')
        content_table = workbook.add_format({'border': 1,'valign':'vcenter'})
        content_table.set_text_wrap()
        content_center = workbook.add_format({'border': 1,'align':'center','valign':'vcenter'})
        content_center.set_text_wrap()
        
        worksheet = workbook.add_worksheet("QoH Product Report")
        worksheet.set_paper(9)
        worksheet.set_portrait()
        worksheet.set_margins(0.5, 0.3, 0.5, 0.5)
        worksheet.freeze_panes(4,0)
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 35)
        worksheet.set_column('C:C', 8)   
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:F', 22)
        
        row = 0
        worksheet.write(row,0,'Quantity On Hand Product Report', bold)
        product_ids = product_obj.search(cr, uid, [('location_id','=',location_id[0])], order='default_code ASC')
                            
        worksheet.write(row+1,0,'Location : ' + report_obj.location_id.complete_name,bold2)
                
        worksheet.write(row+3,0,'Product Code', bold_center)        
        worksheet.write(row+3,1,'Product Name', bold_center)
        worksheet.write(row+3,2,'UOM', bold_center)
        worksheet.write(row+3,3,'Quantity On Hand', bold_center)
        worksheet.write(row+3,4,'Reserved', bold_center)
        worksheet.write(row+3,5,'Available to Reserve', bold_center)
              
        row+=3
        # GET all stock move from stock quant where location same which user choose
        cr.execute("""select sq.product_id,sq.reservation_id from stock_quant sq 
                                    LEFT JOIN stock_move sm 
                                        ON sm.id=sq.reservation_id 
                                            where sq.location_id=%s and sq.product_id in %s""", (location_id[0],tuple(product_ids)))
        all_moves = cr.fetchall()
        for data in product_obj.browse(cr,uid,product_ids,context):
            quant_src = self.pool.get('stock.quant').search(cr, uid, [('product_id.id','=',data.id),('location_id.id','=',location_id[0])])
            qty_on_hand = 0
            for quant in self.pool.get('stock.quant').browse(cr, uid, quant_src, context=context):
                qty_on_hand += quant.qty
            reserved_qty=0
            available_qty=0.0
            moves = [x[1] for x in all_moves if x[0]==data.id]
            boom = self._get_reserved_move(cr, uid, moves, context)
            for move in boom:
                if boom[move]:
                    reserved_qty += boom[move]

            available_qty=qty_on_hand-reserved_qty

            worksheet.write(row+1,0,data.default_code or '',content_center)
            worksheet.write(row+1,1,data.name,content_table)
            worksheet.write(row+1,2,data.uom_id.name or '',content_center)
            worksheet.write(row+1,3,qty_on_hand,content_table)
            worksheet.write(row+1,4,reserved_qty,content_table)
            worksheet.write(row+1,5,available_qty,content_table)
            # change incoiming_qty and outgouing_qty with custom function spesific location
            '''
            incoming : destination loc = location_id[0]
            state not in (draft,done,cancel)
            outgoing : source location = location_id[0]
            state not in (draft,done,cancel)
            '''
#             worksheet.write(row+1,4,data.incoming_qty,content_table)
#             worksheet.write(row+1,5,data.outgoing_qty,content_table)
            row+=1;
        workbook.close()
        out=base64.encodestring(fp.getvalue())
        self.write(cr, uid, ids, {'state_x':'get', 'data_x':out, 'name': filename}, context=context)
        ir_model_data = self.pool.get('ir.model.data')
        fp.close()

        form_res = ir_model_data.get_object_reference(cr, uid, 'pti_stock_report', 'print_qoh_report_view')

        form_id = form_res and form_res[1] or False
        return {
            'name': _('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'qoh.product.report',
            'res_id': ids[0],
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }
product_report()