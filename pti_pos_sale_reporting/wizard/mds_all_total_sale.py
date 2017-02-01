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


class report_mds_all_total_sale(osv.osv_memory):
    _name = "report.mds.all.total.sale"
    
    _columns = {
        'filter' : fields.selection([
            ('1','All'),
            ('2', 'Brand'),
        ],
        track_visibility='onchange', string='Filter'),
        'brand_id' : fields.many2one('product.brand', string="Brand"),
        'state_x': fields.selection( ( ('choose','choose'),('get','get'),)), #xls
        'data_x': fields.binary('File', readonly=True),
        'name': fields.char('Filename', 100, readonly=True),
        'input_type': fields.selection([('list','From List'),('manual','Select Manual')],'Input Type'),
        'date_from' : fields.date('Date', required=True),
        'date_to' : fields.date('Date To', required=True),
    }
    
    _defaults = {
        'state_x': lambda *a: 'choose',
        'filter' : lambda *a: '1',
    }
    
    def mass_assign(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids, context=context)[0]
        ctx = dict(context)
        active_ids = set(context.get('active_ids', []))
        ctx['active_ids'] = list(active_ids)
        print "list active ids",list(active_ids)
        return self.action_apply(cr, uid, ids, context=ctx)
        
    def mds_all_sale_report(self, cr, uid, ids, context=None):
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
        
        check=self.browse(cr,uid,ids,context=context)
        filter_check = self.browse(cr, uid, ids).filter
        if filter_check=='1':
            filename = 'Total Penjualan MDS Nasional.xlsx'
        else:
            brand_id=check.brand_id.id
            brand=check.brand_id.name
            filename = 'Total Penjualan MDS Nasional Per-'+brand+'.xlsx'

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
        
        worksheet = workbook.add_worksheet("Laporan Total Penjualan")
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:C', 30)
        row=0    
        worksheet.merge_range('C1:D1', 'Laporan Total Penjualan', center_title)
        worksheet.write(row+2,0,'Start Period :', bold_left)
        date_fr=datetime.strptime(date_from, '%Y-%m-%d')
        worksheet.write(row+3,0, date_fr.strftime('%d %b %Y'),normal_left)
        worksheet.write(row+2,2,'End Period :', bold_left)
        date_t=datetime.strptime(date_to, '%Y-%m-%d')
        worksheet.write(row+3,2, date_t.strftime('%d %b %Y'),normal_left)
        worksheet.merge_range('D3:E3','Print Date :', bold_left)
        dt=datetime.now()
        worksheet.merge_range('D4:E4', dt.strftime('%d %b %Y %H:%M'),normal_left)
        
        from datetime import timedelta, date
        
        def daterange(start_date, end_date):
            for n in range(int((datetime.strptime(end_date,'%Y-%m-%d')-datetime.strptime(start_date,'%Y-%m-%d')).days)+1):
                yield datetime.strptime(start_date,'%Y-%m-%d') + timedelta(n)
                
        list_date=daterange(date_from,date_to)
        
        def reversed_iterator(lst_iter):
            return reversed(list(lst_iter))
        
        cc=reversed_iterator(list_date)
        if filter_check=='1':
            worksheet.write(row+5,0,'BRAND', header_bold)
            worksheet.write(row+5,1,'DC', header_bold)
            worksheet.write(row+5,2,'STORE NAME', header_bold)
            
            c=3
            for single_date in cc:
                worksheet.set_column(c,c, 12)
                worksheet.write(row+5,c,single_date.strftime("%d-%b-%y"), header_bold)
                c+=1
            worksheet.write(row+5,c,'Grand Total', header_bold)
            worksheet.set_column(c,c, 15)
            
            worksheet.freeze_panes(6,3)
        
            cr.execute(""" 
                    set datestyle=dmy;
                    select distinct pb.id as pb_id , pb.name as pb_name
                    from 
                        (select pc.name as pc_name, pc.tags as pc_id, rp.dc_id as rp_id, sum(po.amount_total_rel) as amount_total
                        from pos_config as pc 
                        join pos_session as ps on pc.id=ps.config_id
                        join pos_order as po on ps.id=po.session_id
                        join product_brand as pb on pb.id=pc.tags
                        join stock_location as sl on sl.id=pc.stock_location_id
                        join res_partner as rp on rp.id=sl.partner_id
                        where po.date_order >= %s and po.date_order <= %s and pc.category_shop='shop_in_shop_mds'
                        group by pc_name, pc_id, rp_id) as pos
                    join product_brand as pb on pb.id=pos.pc_id
                    join res_partner as rpdc on rpdc.id=pos.rp_id
                    """, (date_from+' 00:00:00', date_to+' 23:59:59'))
            num_brand = cr.fetchall()
            rows=row+7
            
            for res in num_brand:
                pb_id = res[0]
                pb_name = res[1]
                cr.execute(""" 
                    set datestyle=dmy;
                    select pcid, rpdc.name as dc_name, pos.pc_name as pc_name
                    from 
                        (select pc.id as pcid , pc.name as pc_name, pc.tags as pc_id, rp.dc_id as rp_id, sum(po.amount_total_rel) as amount_total
                        from pos_config as pc 
                        join pos_session as ps on pc.id=ps.config_id
                        join pos_order as po on ps.id=po.session_id
                        join product_brand as pb on pb.id=pc.tags
                        join stock_location as sl on sl.id=pc.stock_location_id
                        join res_partner as rp on rp.id=sl.partner_id
                        where po.date_order >= %s and po.date_order <= %s and pc.category_shop = 'shop_in_shop_mds'
                        group by pc_name, pc_id, rp_id,pcid) as pos
                    join product_brand as pb on pb.id=pos.pc_id
                    join res_partner as rpdc on rpdc.id=pos.rp_id
                    where pb.id=%s
                    """, (date_from+' 00:00:00', date_to+' 23:59:59',pb_id))
                name_brand = cr.fetchall()
                brand_length=len(name_brand)
                total_per_day=0
                
                if brand_length==1:
                    c=-1
                    worksheet.write(rows-1,0, pb_name, header_style)
                    
                    for order in name_brand:
                        worksheet.write(rows-1,1, name_brand[0][1], header_style)
                        worksheet.write(rows-1,2, name_brand[0][2], header_style)
                        single_dt=daterange(date_from, date_to)
                        cc1=reversed_iterator(single_dt)
                        sdt=0
                        single_grand_tot=0
                        
                        for l in cc1:
                            cr.execute(""" 
                                set datestyle=dmy;
                                select pb.name as pb_name, rpdc.name as dc_name, pos.pc_name as pc_name, pos.amount_total as amount_total
                                from 
                                    (select pc.name as pc_name, pc.tags as pc_id, rp.dc_id as rp_id, coalesce(sum(po.amount_total_rel),0) as amount_total
                                    from pos_config as pc 
                                    join pos_session as ps on pc.id=ps.config_id
                                    join pos_order as po on ps.id=po.session_id
                                    join product_brand as pb on pb.id=pc.tags
                                    join stock_location as sl on sl.id=pc.stock_location_id
                                    join res_partner as rp on rp.id=sl.partner_id
                                    where po.date_order >= %s and po.date_order <= %s and pc.id=%s and pc.category_shop = 'shop_in_shop_mds'
                                    group by pc_name, pc_id, rp_id) as pos
                                join product_brand as pb on pb.id=pos.pc_id
                                join res_partner as rpdc on rpdc.id=pos.rp_id
                                where pb.id=%s
                                """, (l.strftime("%d-%m-%y")+' 00:00:00',l.strftime("%d-%m-%y")+' 23:59:59',name_brand[0][0],pb_id))
                            total_date = cr.fetchall()
                            if total_date:
                                worksheet.write(rows-1,3+sdt, total_date[0][3], header_right)
                                single_grand_tot+=total_date[0][3]
                            elif not total_date:
                                worksheet.write(rows-1,3+sdt, "", header_right)
                            sdt+=1
                        worksheet.write(rows-1,3+sdt, single_grand_tot, header_right)
                        c+=1
                    grand_dt1=daterange(date_from, date_to)
                    cc_grand1=reversed_iterator(grand_dt1)
                    gdt1=0
                    gdt_tot1=0
                    
                    for n in cc_grand1:
                        print n.strftime("%d-%m-%y")
                        cr.execute("""
                        set datestyle=dmy;
                        select coalesce(sum(temp.amount_total),0) from
                            (select pb.name as pb_name, rpdc.name as dc_name, pos.pc_name as pc_name, pos.amount_total as amount_total
                            from 
                                (select pc.name as pc_name, pc.tags as pc_id, rp.dc_id as rp_id, coalesce(sum(po.amount_total_rel),0) as amount_total
                                from pos_config as pc 
                                join pos_session as ps on pc.id=ps.config_id
                                join pos_order as po on ps.id=po.session_id
                                join product_brand as pb on pb.id=pc.tags
                                join stock_location as sl on sl.id=pc.stock_location_id
                                join res_partner as rp on rp.id=sl.partner_id
                                where po.date_order >= %s and po.date_order <= %s and pc.category_shop = 'shop_in_shop_mds'
                                group by pc_name, pc_id, rp_id, pc.tags) as pos
                            join product_brand as pb on pb.id=pos.pc_id
                            join res_partner as rpdc on rpdc.id=pos.rp_id
                            where pb.id=%s) as temp
                        """, (n.strftime("%d-%m-%y")+' 00:00:00',n.strftime("%d-%m-%y")+' 23:59:59',pb_id))
                        grand_brand = cr.fetchall()
                        if grand_brand:
                            worksheet.write(rows,3+gdt1, grand_brand[0][0], header_bold_right)
                            gdt_tot1+=grand_brand[0][0]
                        elif grand_brand:
                            worksheet.write(rows,3+gdt1, "", header_bold_right)
                        gdt1+=1
                    worksheet.merge_range('A'+str(rows+1)+':C'+str(rows+1), pb_name+" Total", header_bold)
                    worksheet.write(rows,3+gdt1, gdt_tot1, header_bold_right)
                    rows+=1
                    
                elif brand_length>1:
                    worksheet.merge_range('A'+str(rows)+':A'+str(rows+brand_length-1), pb_name, header_style)
                    c=0
                    
                    for order in name_brand:
                        worksheet.write(rows-1+c,1, name_brand[c][1], header_style)
                        worksheet.write(rows-1+c,2, name_brand[c][2], header_style)
                        list_dt=daterange(date_from,date_to)
                        cc2=reversed_iterator(list_dt)
                        cdt=0
                        grand_tot=0
                        
                        for m in cc2:
                            cr.execute(""" 
                                set datestyle=dmy;
                                select pb.name as pb_name, rpdc.name as dc_name, pos.pc_name as pc_name, pos.amount_total as amount_total
                                from 
                                    (select pc.name as pc_name, pc.tags as pc_id, rp.dc_id as rp_id, coalesce(sum(po.amount_total_rel),0) as amount_total
                                    from pos_config as pc 
                                    join pos_session as ps on pc.id=ps.config_id
                                    join pos_order as po on ps.id=po.session_id
                                    join product_brand as pb on pb.id=pc.tags
                                    join stock_location as sl on sl.id=pc.stock_location_id
                                    join res_partner as rp on rp.id=sl.partner_id
                                    where po.date_order >= %s and po.date_order <= %s and pc.id=%s and pc.category_shop = 'shop_in_shop_mds'
                                    group by pc_name, pc_id, rp_id) as pos
                                join product_brand as pb on pb.id=pos.pc_id
                                join res_partner as rpdc on rpdc.id=pos.rp_id
                                where pb.id=%s
                                """, (m.strftime("%d-%m-%y")+' 00:00:00',m.strftime("%d-%m-%y")+' 23:59:59',name_brand[c][0],pb_id))
                            total_date = cr.fetchall()
                            if total_date:
                                worksheet.write(rows-1+c,3+cdt, total_date[0][3], header_right)
                                grand_tot+=total_date[0][3]
                            elif not total_date:
                                worksheet.write(rows-1+c,3+cdt, "", header_right)
                            cdt+=1
                        worksheet.write(rows-1+c,3+cdt, grand_tot, header_right)
                        c+=1
                    grand_dt2=daterange(date_from, date_to)
                    cc_grand2=reversed_iterator(grand_dt2)
                    gdt2=0
                    gdt_tot2=0
                    
                    for n in cc_grand2:
                        cr.execute("""
                        set datestyle=dmy;
                        select coalesce(sum(temp.amount_total),0) from
                            (select pb.name as pb_name, rpdc.name as dc_name, pos.pc_name as pc_name, pos.amount_total as amount_total
                            from 
                                (select pc.name as pc_name, pc.tags as pc_id, rp.dc_id as rp_id, sum(po.amount_total_rel) as amount_total
                                from pos_config as pc 
                                join pos_session as ps on pc.id=ps.config_id
                                join pos_order as po on ps.id=po.session_id
                                join product_brand as pb on pb.id=pc.tags
                                join stock_location as sl on sl.id=pc.stock_location_id
                                join res_partner as rp on rp.id=sl.partner_id
                                where po.date_order >= %s and po.date_order <= %s and pc.category_shop = 'shop_in_shop_mds'
                                group by pc_name, pc_id, rp_id) as pos
                            join product_brand as pb on pb.id=pos.pc_id
                            join res_partner as rpdc on rpdc.id=pos.rp_id
                            where pb.id=%s) as temp
                        """, (n.strftime("%d-%m-%y")+' 00:00:00',n.strftime("%d-%m-%y")+' 23:59:59',pb_id))
                        grand_brand = cr.fetchall()
                        if grand_brand:
                            worksheet.write(rows-1+c,3+gdt2, grand_brand[0][0], header_bold_right)
                            gdt_tot2+=grand_brand[0][0]
                        elif grand_brand:
                            worksheet.write(rows-1+c,3+gdt2, "", header_bold_right)
                        gdt2+=1
                    worksheet.merge_range('A'+str(rows+c)+':C'+str(rows+c), pb_name+" Total", header_bold)
                    worksheet.write(rows-1+c,3+gdt2, gdt_tot2, header_bold_right)
                rows+=1
                
            grand_day=daterange(date_from, date_to)
            cc_grandday=reversed_iterator(grand_day)
            granddt=0
            gdt_totday=0
                
            for o in cc_grandday:
                cr.execute("""
                set datestyle=dmy;
                select coalesce(sum(temp.amount_total),0) from
                    (select pb.name as pb_name, rpdc.name as dc_name, pos.pc_name as pc_name, pos.amount_total as amount_total
                    from 
                        (select pc.name as pc_name, pc.tags as pc_id, rp.dc_id as rp_id, sum(po.amount_total_rel) as amount_total
                        from pos_config as pc 
                        join pos_session as ps on pc.id=ps.config_id
                        join pos_order as po on ps.id=po.session_id
                        join product_brand as pb on pb.id=pc.tags
                        join stock_location as sl on sl.id=pc.stock_location_id
                        join res_partner as rp on rp.id=sl.partner_id
                        where po.date_order >= %s and po.date_order <= %s and pc.category_shop = 'shop_in_shop_mds'
                        group by pc_name, pc_id, rp_id,pc.tags) as pos
                    join product_brand as pb on pb.id=pos.pc_id
                    join res_partner as rpdc on rpdc.id=pos.rp_id) as temp
                """, (o.strftime("%d-%m-%y")+' 00:00:00',o.strftime("%d-%m-%y")+' 23:59:59'))
                totalday=cr.fetchall()
                if totalday:
                    print totalday[0][0]
                    worksheet.write(rows-1+c,3+granddt, totalday[0][0], header_bold_right)
                    gdt_totday+=totalday[0][0]
                elif totalday:
                    worksheet.write(rows-1+c,3+granddt, "", header_bold_right)
                granddt+=1
            worksheet.merge_range('A'+str(rows+c)+':C'+str(rows+c), "Grand Total", header_bold)
            worksheet.write(rows-1+c,3+granddt, gdt_totday, header_bold_right)
                
                    
            workbook.close()
        
        else:
            
            worksheet.write(row+5,0,'BRAND', header_bold)
            worksheet.write(row+5,1,'DC', header_bold)
            worksheet.write(row+5,2,'STORE NAME', header_bold)
            
            c=3
            for single_date in cc:
                worksheet.set_column(c,c, 12)
                worksheet.write(row+5,c,single_date.strftime("%d-%b-%y"), header_bold)
                c+=1
            worksheet.write(row+5,c,'Grand Total', header_bold)
            worksheet.set_column(c,c, 15)
            
            worksheet.freeze_panes(6,3)
        
            cr.execute(""" 
                    set datestyle=dmy;
                    select distinct pb.id as pb_id ,pb.name as pb_name
                    from 
                        (select pc.name as pc_name, pc.tags as pc_id, rp.dc_id as rp_id, sum(po.amount_total_rel) as amount_total
                        from pos_config as pc 
                        join pos_session as ps on pc.id=ps.config_id
                        join pos_order as po on ps.id=po.session_id
                        join product_brand as pb on pb.id=pc.tags
                        join stock_location as sl on sl.id=pc.stock_location_id
                        join res_partner as rp on rp.id=sl.partner_id
                        where po.date_order >= %s and po.date_order <= %s and pc.tags=%s and pc.category_shop='shop_in_shop_mds'
                        group by pc_name, pc_id, rp_id,pc.tags) as pos
                    join product_brand as pb on pb.id=pos.pc_id
                    join res_partner as rpdc on rpdc.id=pos.rp_id
                    """, (date_from+' 00:00:00', date_to+' 23:59:59',brand_id))
            num_brand = cr.fetchall()
            rows=row+7
            
            for res in num_brand:
                pb_id = res[0]
                pb_name = res[1]
                cr.execute(""" 
                    set datestyle=dmy;
                    select pb.id as pb_id, rpdc.name as dc_name, pos.pcid as pc_id, pos.pc_name as pc_name
                    from 
                        (select pc.name as pc_name, pc.id as pcid,pc.tags as pc_id, rp.dc_id as rp_id, sum(po.amount_total_rel) as amount_total
                        from pos_config as pc 
                        join pos_session as ps on pc.id=ps.config_id
                        join pos_order as po on ps.id=po.session_id
                        join product_brand as pb on pb.id=pc.tags
                        join stock_location as sl on sl.id=pc.stock_location_id
                        join res_partner as rp on rp.id=sl.partner_id
                        where po.date_order >= %s and po.date_order <= %s and pc.tags=%s and pc.category_shop = 'shop_in_shop_mds'
                        group by pc_name, pc_id, rp_id,pc.tags,pcid) as pos
                    join product_brand as pb on pb.id=pos.pc_id
                    join res_partner as rpdc on rpdc.id=pos.rp_id
                    where pb.id=%s
                    """, (date_from+' 00:00:00', date_to+' 23:59:59',pb_id,pb_id))
                name_brand = cr.fetchall()
                brand_length=len(name_brand)
                total_per_day=0
                
                if brand_length==1:
                    c=-1
                    worksheet.write(rows-1,0, pb_name, header_style)
                    
                    for order in name_brand:
                        worksheet.write(rows-1,1, name_brand[0][1], header_style)
                        worksheet.write(rows-1,2, name_brand[0][3], header_style)
                        single_dt=daterange(date_from, date_to)
                        cc1=reversed_iterator(single_dt)
                        sdt=0
                        single_grand_tot=0
                        
                        for l in cc1:
                            cr.execute(""" 
                                set datestyle=dmy;
                                select pb.name as pb_name, rpdc.name as dc_name, pos.pc_name as pc_name, pos.amount_total as amount_total
                                from 
                                    (select pc.name as pc_name, pc.tags as pc_id, rp.dc_id as rp_id, coalesce(sum(po.amount_total_rel),0) as amount_total
                                    from pos_config as pc 
                                    join pos_session as ps on pc.id=ps.config_id
                                    join pos_order as po on ps.id=po.session_id
                                    join product_brand as pb on pb.id=pc.tags
                                    join stock_location as sl on sl.id=pc.stock_location_id
                                    join res_partner as rp on rp.id=sl.partner_id
                                    where po.date_order >= %s and po.date_order <= %s and pc.id=%s and pc.tags=%s and pc.category_shop = 'shop_in_shop_mds'
                                    group by pc_name, pc_id, rp_id,pc.tags) as pos
                                join product_brand as pb on pb.id=pos.pc_id
                                join res_partner as rpdc on rpdc.id=pos.rp_id
                                where pb.id=%s
                                """, (l.strftime("%d-%m-%y")+' 00:00:00',l.strftime("%d-%m-%y")+' 23:59:59',name_brand[0][2],pb_id,pb_id))
                            total_date = cr.fetchall()
                            if total_date:
                                worksheet.write(rows-1,3+sdt, total_date[0][3], header_right)
                                single_grand_tot+=total_date[0][3]
                            elif not total_date:
                                worksheet.write(rows-1,3+sdt, "", header_right)
                            sdt+=1
                        worksheet.write(rows-1,3+sdt, single_grand_tot, header_right)
                        c+=1
                    grand_dt1=daterange(date_from, date_to)
                    cc_grand1=reversed_iterator(grand_dt1)
                    gdt1=0
                    gdt_tot1=0
                    
                    for n in cc_grand1:
                        print n.strftime("%d-%m-%y")
                        cr.execute("""
                        set datestyle=dmy;
                        select coalesce(sum(temp.amount_total),0) from
                            (select pb.name as pb_name, rpdc.name as dc_name, pos.pc_name as pc_name, pos.amount_total as amount_total
                            from 
                                (select pc.name as pc_name, pc.tags as pc_id, rp.dc_id as rp_id, coalesce(sum(po.amount_total_rel),0) as amount_total
                                from pos_config as pc 
                                join pos_session as ps on pc.id=ps.config_id
                                join pos_order as po on ps.id=po.session_id
                                join product_brand as pb on pb.id=pc.tags
                                join stock_location as sl on sl.id=pc.stock_location_id
                                join res_partner as rp on rp.id=sl.partner_id
                                where po.date_order >= %s and po.date_order <= %s and pc.tags=%s and pc.category_shop = 'shop_in_shop_mds'
                                group by pc_name, pc_id, rp_id, pc.tags) as pos
                            join product_brand as pb on pb.id=pos.pc_id
                            join res_partner as rpdc on rpdc.id=pos.rp_id
                            where pb.id=%s) as temp
                        """, (n.strftime("%d-%m-%y")+' 00:00:00',n.strftime("%d-%m-%y")+' 23:59:59',pb_id,pb_id))
                        grand_brand = cr.fetchall()
                        if grand_brand:
                            worksheet.write(rows,3+gdt1, grand_brand[0][0], header_bold_right)
                            gdt_tot1+=grand_brand[0][0]
                        elif grand_brand:
                            worksheet.write(rows,3+gdt1, "", header_bold_right)
                        gdt1+=1
                    worksheet.merge_range('A'+str(rows+1)+':C'+str(rows+1), pb_name+" Total", header_bold)
                    worksheet.write(rows,3+gdt1, gdt_tot1, header_bold_right)
                    
                    rows+=1
                    
                    
                elif brand_length>1:
                    worksheet.merge_range('A'+str(rows)+':A'+str(rows+brand_length-1), pb_name, header_style)
                    c=0
                    
                    for order in name_brand:
                        print name_brand[c][2]
                        worksheet.write(rows-1+c,1, name_brand[c][1], header_style)
                        worksheet.write(rows-1+c,2, name_brand[c][3], header_style)
                        list_dt=daterange(date_from,date_to)
                        cc2=reversed_iterator(list_dt)
                        cdt=0
                        grand_tot=0
                        
                        for m in cc2:
                            print 'satu kali'
                            cr.execute(""" 
                                set datestyle=dmy;
                                select pb.name as pb_name, rpdc.name as dc_name, pos.pc_name as pc_name, pos.amount_total as amount_total
                                from 
                                    (select pc.name as pc_name, pc.tags as pc_id, rp.dc_id as rp_id, coalesce(sum(po.amount_total_rel),0) as amount_total
                                    from pos_config as pc 
                                    join pos_session as ps on pc.id=ps.config_id
                                    join pos_order as po on ps.id=po.session_id
                                    join product_brand as pb on pb.id=pc.tags
                                    join stock_location as sl on sl.id=pc.stock_location_id
                                    join res_partner as rp on rp.id=sl.partner_id
                                    where po.date_order >= %s and po.date_order <= %s and pc.id=%s and pc.tags=%s and pc.category_shop = 'shop_in_shop_mds'
                                    group by pc_name, pc_id, rp_id) as pos
                                join product_brand as pb on pb.id=pos.pc_id
                                join res_partner as rpdc on rpdc.id=pos.rp_id
                                where pb.id=%s
                                """, (m.strftime("%d-%m-%y")+' 00:00:00',m.strftime("%d-%m-%y")+' 23:59:59',name_brand[c][2],brand_id,pb_id))
                            total_date = cr.fetchall()
                            print total_date
                            if total_date:
                                worksheet.write(rows-1+c,3+cdt, total_date[0][3], header_right)
                                grand_tot+=total_date[0][3]
                            elif not total_date:
                                worksheet.write(rows-1+c,3+cdt, "", header_right)
                            cdt+=1
                        worksheet.write(rows-1+c,3+cdt, grand_tot, header_right)
                        c+=1
                    grand_dt2=daterange(date_from, date_to)
                    cc_grand2=reversed_iterator(grand_dt2)
                    gdt2=0
                    gdt_tot2=0
                    
                    for n in cc_grand2:
                        cr.execute("""
                        set datestyle=dmy;
                        select coalesce(sum(temp.amount_total),0) from
                            (select pb.name as pb_name, rpdc.name as dc_name, pos.pc_name as pc_name, pos.amount_total as amount_total
                            from 
                                (select pc.name as pc_name, pc.tags as pc_id, rp.dc_id as rp_id, sum(po.amount_total_rel) as amount_total
                                from pos_config as pc 
                                join pos_session as ps on pc.id=ps.config_id
                                join pos_order as po on ps.id=po.session_id
                                join product_brand as pb on pb.id=pc.tags
                                join stock_location as sl on sl.id=pc.stock_location_id
                                join res_partner as rp on rp.id=sl.partner_id
                                where po.date_order >= %s and po.date_order <= %s and pc.tags=%s and pc.category_shop = 'shop_in_shop_mds'
                                group by pc_name, pc_id, rp_id, pc.tags) as pos
                            join product_brand as pb on pb.id=pos.pc_id
                            join res_partner as rpdc on rpdc.id=pos.rp_id
                            where pb.id=%s) as temp
                        """, (n.strftime("%d-%m-%y")+' 00:00:00',n.strftime("%d-%m-%y")+' 23:59:59',brand_id,pb_id))
                        grand_brand = cr.fetchall()
                        if grand_brand:
                            worksheet.write(rows-1+c,3+gdt2, grand_brand[0][0], header_bold_right)
                            gdt_tot2+=grand_brand[0][0]
                        elif grand_brand:
                            worksheet.write(rows-1+c,3+gdt2, "", header_bold_right)
                        gdt2+=1
                    worksheet.merge_range('A'+str(rows+c)+':C'+str(rows+c), pb_name+" Total", header_bold)
                    worksheet.write(rows-1+c,3+gdt2, gdt_tot2, header_bold_right)
                rows+=1
                
            grand_day=daterange(date_from, date_to)
            cc_grandday=reversed_iterator(grand_day)
            granddt=0
            gdt_totday=0
                
            for o in cc_grandday:
                cr.execute("""
                set datestyle=dmy;
                select coalesce(sum(temp.amount_total),0) from
                    (select pb.name as pb_name, rpdc.name as dc_name, pos.pc_name as pc_name, pos.amount_total as amount_total
                    from 
                        (select pc.name as pc_name, pc.tags as pc_id, rp.dc_id as rp_id, sum(po.amount_total_rel) as amount_total
                        from pos_config as pc 
                        join pos_session as ps on pc.id=ps.config_id
                        join pos_order as po on ps.id=po.session_id
                        join product_brand as pb on pb.id=pc.tags
                        join stock_location as sl on sl.id=pc.stock_location_id
                        join res_partner as rp on rp.id=sl.partner_id
                        where po.date_order >= %s and po.date_order <= %s and pc.tags=%s and pc.category_shop = 'shop_in_shop_mds'
                        group by pc_name, pc_id, rp_id,pc.tags) as pos
                    join product_brand as pb on pb.id=pos.pc_id
                    join res_partner as rpdc on rpdc.id=pos.rp_id) as temp
                """, (o.strftime("%d-%m-%y")+' 00:00:00',o.strftime("%d-%m-%y")+' 23:59:59',brand_id))
                totalday=cr.fetchall()
                if totalday:
                    worksheet.write(rows-1+c,3+granddt, totalday[0][0], header_bold_right)
                    gdt_totday+=totalday[0][0]
                elif totalday:
                    worksheet.write(rows-1+c,3+granddt, "", header_bold_right)
                granddt+=1
            worksheet.merge_range('A'+str(rows+c)+':C'+str(rows+c), "Grand Total", header_bold)
            worksheet.write(rows-1+c,3+granddt, gdt_totday, header_bold_right)
                
                    
            workbook.close()
        
        out=base64.encodestring(fp.getvalue())
        self.write(cr, uid, ids, {'state_x':'get', 'data_x':out, 'name': filename}, context=context)
        ir_model_data = self.pool.get('ir.model.data')
        fp.close()
 
        form_res = ir_model_data.get_object_reference(cr, uid, 'pti_pos_sale_reporting', 'report_mds_all_total_sale_view')
 
        form_id = form_res and form_res[1] or False
        return {
            'name': _('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'report.mds.all.total.sale',
            'res_id': ids[0],
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }