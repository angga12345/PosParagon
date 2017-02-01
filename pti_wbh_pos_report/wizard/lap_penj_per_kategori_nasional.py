#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import time
import logging
import base64
import xlwt
from xlwt import *
from io import BytesIO
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


class report_wbh_store_category_national(osv.osv_memory):
    _name = "report.wbh.store.category.national"
    
    _columns = {
        'state_x': fields.selection( ( ('choose','choose'),('get','get'),)), #xls
        'data_x': fields.binary('File', readonly=True),
        'name': fields.char('Filename', 100, readonly=True),
        'input_type': fields.selection([('list','From List'),('manual','Select Manual')],'Input Type'),
        'date_from' : fields.date('Date', required=True),
        'date_to' : fields.date('Date To', required=True),
    }
    
    _defaults = {
        'state_x': lambda *a: 'choose',
    }
    
    def mass_assign(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids, context=context)[0]
        ctx = dict(context)
        active_ids = set(context.get('active_ids', []))
        ctx['active_ids'] = list(active_ids)
        return self.action_apply(cr, uid, ids, context=ctx)
    
    def take_value_product(self,cr,uid,ids,date_from, date_to, context=None):
        cr.execute("""
        select distinct
            temp.store, pt.name, temp.price_unit, sum(temp.qty) as Qty, sum(temp.price) as Nominal, temp.discount, pt.id
        from
            (select 
            pc.name as store, prod.id, prod.product_tmpl_id, pol.qty, pol.price_unit, pol.price_subtotal_rel as price, pol.discount as discount
            from 
            pos_order_line as pol
            join 
            pos_order as po on po.id=pol.order_id
            join
            pos_session as ps on ps.id=po.session_id
            join
            pos_config as pc on pc.id=ps.config_id
            join 
            product_product as prod on prod.id=pol.product_id
            where
            po.date_order >= %s and po.date_order <= %s and pc.category_shop='stand_alone' and pc.stand_alone_categ='wbh' and pol.price_unit > 0) as temp
        join
            product_template as pt on pt.id=temp.product_tmpl_id
        group by
            pt.name, temp.id, temp.price_unit, temp.discount, temp.store, pt.id
        order by
            pt.name
        """,(date_from+' 00:00:00', date_to+' 23:59:59'))
        prod_param=cr.fetchall()
        return prod_param
    
    def take_value_categ(self,cr,uid,ids,product_name,context=None):
        cr.execute("""
        select pt.name as product, ppc.name as category
            from product_template as pt
            join pos_product_category_product_template_rel as ppcpt on pt.id = ppcpt.product_template_id
            join pos_product_category as ppc on ppc.id = ppcpt.pos_product_category_id
            where pt.id=%s
            order by pt.name
        """,(product_name,))
        categ=cr.fetchall()
        return categ
    
    
    def wbh_store_category_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         data['form'] = self.read(cr, uid, ids, parcel_ids, context=context)[0]
        data = {}
        data['form'] = self.read(cr, uid, ids, ['date_from','date_to'], context=context)[0]
        return self._excel_report(cr, uid, ids, data, context=context)
            
    def _excel_report(self, cr, uid, ids, data, context=None):
        ship_obj = self.pool.get('cargo')
        active_ids = set(context.get('active_ids', []))
        fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        pos=self.browse(cr,uid,ids,context=context)
        filename = 'Laporan Penjualan Per Kategori WBH Nasional.xlsx'
        
        #### STYLE
        #################################################################################
        center_title = workbook.add_format({'bold': 1,'valign':'vcenter','align':'center'})
        center_title.set_text_wrap()
        center_title.set_font_name('Arial')
        center_title.set_font_size('12')
        #################################################################################
        normal_left = workbook.add_format({'valign':'bottom','align':'left'})
        normal_left.set_text_wrap()
        normal_left.set_font_name('Arial')
        normal_left.set_font_size('10')
        #################################################################################
        bold_left = workbook.add_format({'bold': 1,'valign':'vcenter','align':'left'})
        bold_left.set_text_wrap()
        bold_left.set_font_name('Arial')
        bold_left.set_font_size('10')
        #################################################################################
        normal_bold = workbook.add_format({'bold': 1,'valign':'vcenter','align':'center'})
        normal_bold.set_text_wrap()
        normal_bold.set_font_name('Arial')
        normal_bold.set_font_size('10')
        #################################################################################
        header_style = workbook.add_format({'align':'left','valign':'vcenter'})
        header_style.set_font_name('Arial')
        header_style.set_font_size('10')
        header_style.set_text_wrap()
        header_style.set_border()
        #################################################################################
        header_right = workbook.add_format({'align':'right','valign':'vcenter'})
        header_right.set_font_name('Arial')
        header_right.set_font_size('10')
        header_right.set_text_wrap()
        header_right.set_border()
        header_right.set_num_format('#,##0.00')
        #################################################################################
        header_bold_right = workbook.add_format({'bold': 1,'align':'right','valign':'vcenter'})
        header_bold_right.set_font_name('Arial')
        header_bold_right.set_font_size('10')
        header_bold_right.set_text_wrap()
        header_bold_right.set_border()
        header_bold_right.set_num_format('#,##0.00')
        #################################################################################
        header_bold = workbook.add_format({'bold': 1,'align':'center','valign':'vcenter'})
        header_bold.set_font_name('Arial')
        header_bold.set_font_size('10')
        header_bold.set_text_wrap()
        header_bold.set_border()
        #################################################################################
        header_center_bold = workbook.add_format({'bold': 1,'align':'left','valign':'vcenter'})
        header_center_bold.set_font_name('Arial')
        header_center_bold.set_font_size('10')
        header_center_bold.set_text_wrap()
        header_center_bold.set_border()
        #################################################################################
        format_number = workbook.add_format({'valign':'vcenter','align':'right'})
        format_number.set_num_format('#,##0.00')
        format_number.set_font_name('Arial')
        format_number.set_font_size('10')
        format_number.set_border()
        #################################################################################
        normal_center_border = workbook.add_format({'valign':'center','align':'center'})
        normal_center_border.set_text_wrap()
        normal_center_border.set_font_name('Arial')
        normal_center_border.set_font_size('10')
        normal_center_border.set_border()
        #################################################################################
        
        worksheet = workbook.add_worksheet("Laporan Penjualan Per Kategori")
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 45)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 7)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 7)
        worksheet.set_column('K:K', 15)
        worksheet.set_column('L:L', 22)
        row=0    
        worksheet.merge_range('C1:E1', 'Laporan Penjualan Per Kategori', center_title)
        worksheet.merge_range('A3:B3','Start Period :', bold_left)
        date_fr=datetime.strptime(date_from, '%Y-%m-%d')
        worksheet.merge_range('A4:B4', date_fr.strftime('%d %b %Y'),normal_left)
        worksheet.write(row+2,2,'End Period :', bold_left)
        date_t=datetime.strptime(date_to, '%Y-%m-%d')
        worksheet.write(row+3,2, date_t.strftime('%d %b %Y'),normal_left)
        worksheet.write(row+2,4,'Print Date :', bold_left)
        dt=datetime.now()
        worksheet.write(row+3,4, dt.strftime('%d %b %Y %H:%M'),normal_left)
        
        worksheet.write(row+5,0,'No.', header_bold)
        worksheet.write(row+5,1,'Product', header_bold)
        worksheet.write(row+5,2,'Price', header_bold)
        worksheet.write(row+5,3,'Kategori 1', header_bold)
        worksheet.write(row+5,4,'Kategori 2', header_bold)
        worksheet.write(row+5,5,'Kategori 3', header_bold)
        worksheet.write(row+5,6,'Kategori 4', header_bold)
        worksheet.write(row+5,7,'Qty', header_bold)
        worksheet.write(row+5,8,'Nominal Rp', header_bold)
        worksheet.write(row+5,9,'% Disc.', header_bold)
        worksheet.write(row+5,10,'Nominal Disc', header_bold)
        worksheet.write(row+5,11,'Nominal Setelah Disc.', header_bold)
        
        worksheet.freeze_panes(6,3)
        rows=row+7
        prod_param  = self.take_value_product(cr,uid,ids,date_from, date_to, context=context)
        print prod_param
 
        i=1
        for prod in prod_param:
            worksheet.write(rows-1,0, i, normal_center_border)
            if len(prod[1])>45:
                worksheet.set_row(rows-1,30)
                worksheet.write(rows-1,1, prod[1], header_style)
            elif len(prod[1])<=45:
                worksheet.write(rows-1,1, prod[1], header_style)
            worksheet.write(rows-1,2, prod[2], format_number)
            worksheet.write(rows-1,7, prod[3], format_number)
            v=(prod[3] * prod[2])
            worksheet.write(rows-1,8, v, format_number )
            worksheet.write(rows-1,9, prod[5], format_number)
            disc_value = (v * prod[5])/100
            worksheet.write(rows-1,10, disc_value, format_number)
            worksheet.write(rows-1,11, prod[4], format_number)
            
            product_name=prod[6]
            
            categ= self.take_value_categ(cr,uid,ids,product_name,context=context)
            print "categ fetch",categ
            j=0
            
            m=4
            
            li=len(categ)
            li_diff = m - li
            
            for m in range(li_diff):
                categ.append(())
                
            print "new categ",categ
            
            for k in categ:
                print "k",k
                if k:
                    if len(k[1])>20:
                        worksheet.set_row(rows-1,30)
                        worksheet.write(rows-1,j+3, k[1], header_style)
                    elif len(k[1])<=20:
                        worksheet.write(rows-1,j+3, k[1], header_style)
                elif not k:
                    worksheet.write(rows-1,j+3, "-", normal_center_border)
                j+=1
#             for categ_name in categ:
#                 print "categ",categ_name
#                 if categ_name[1]:
#                     worksheet.write(rows-1,j+3, categ_name[1], header_style)
#                 elif not categ_name[1]:
#                     worksheet.write(rows-1,j+3, " ", header_style)
#                 j+=1
            i+=1
            rows+=1
        
                
        workbook.close()
        
        out=base64.encodestring(fp.getvalue())
        self.write(cr, uid, ids, {'state_x':'get', 'data_x':out, 'name': filename}, context=context)
        ir_model_data = self.pool.get('ir.model.data')
        fp.close()
 
        form_res = ir_model_data.get_object_reference(cr, uid, 'pti_wbh_pos_report', 'report_wbh_store_category_national_view')
 
        form_id = form_res and form_res[1] or False
        return {
            'name': _('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'report.wbh.store.category.national',
            'res_id': ids[0],
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }