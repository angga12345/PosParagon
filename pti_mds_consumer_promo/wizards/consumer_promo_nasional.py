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

import xlsxwriter
import base64
from openerp import models, fields, api
from cStringIO import StringIO
from datetime import datetime, timedelta


class ConsumerPromoReport(models.TransientModel):
    _name = "consumer.promo.nasional.wizard"
    
    filter = fields.Selection((('1','All'),('2', 'Brand')), string='Filter', default='1')
    brand_id = fields.Many2one('product.brand','Brand')
    
    end_period = fields.Date(string="End Period")
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    Date = fields.Date('Date') 

    @api.multi
    def generate_excel_consumer_nasional(self):
        bz = StringIO()
        workbook =  xlsxwriter.Workbook(bz)
        date = datetime.strptime(self.Date,'%Y-%m-%d')
        take_year = datetime.strftime(date,'%Y')          #date change to string
        take_month= datetime.strftime(date,'%m')
        year = date.year
        month = date.month
        
        print'integer',month , year
        print'str',take_month , take_year
        
        month_dict = {  
                        1 : 'January',2:'February',3:'March',4:'April',5:'May',6:'June',
                        7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'
                     }
        
        month_check = month_dict[month]
        
        filter_check = self.filter
        if filter_check == '1': 
            filename = 'Laporan Consumer Promo MDS Nasional Bulan: '+month_check+'.xlsx'
            brand = 'All'
        else:
            brand_id = self.brand_id.id
            brand = self.brand_id.name
            filename = 'Laporan Consumer Promo MDS Nasional Brand: '+brand+', Bulan: '+month_check+'.xlsx'
            
        #### STYLE
        #################################################################################
        center_title = workbook.add_format({'bold': 1,'valign':'vcenter','align':'center'})
        center_title.set_text_wrap()
        center_title.set_font_name('Arial')
        center_title.set_font_size('14')
        #################################################################################
        normal_left = workbook.add_format({'valign':'bottom','align':'left'})
        normal_left.set_text_wrap()
        normal_left.set_font_name('Arial')
        normal_left.set_font_size('10')
        normal_left.set_border()
        #################################################################################
        normal_left_unborder = workbook.add_format({'valign':'bottom','align':'left'})
        normal_left_unborder.set_text_wrap()
        normal_left_unborder.set_font_name('Arial')
        normal_left_unborder.set_font_size('10')
        #################################################################################
        normal_left_unborder_bold = workbook.add_format({'bold':1, 'valign':'bottom','align':'left'})
        normal_left_unborder_bold.set_text_wrap()
        normal_left_unborder_bold.set_font_name('Arial')
        normal_left_unborder_bold.set_font_size('10')        
        #################################################################################
        normal_center = workbook.add_format({'valign':'bottom','align':'center'})
        normal_center.set_text_wrap()
        normal_center.set_font_name('Arial')
        normal_center.set_font_size('10')
        normal_center.set_border()        
        #################################################################################
        normal_right = workbook.add_format({'valign':'bottom','align':'right'})
        normal_right.set_text_wrap()
        normal_right.set_font_name('Arial')
        normal_right.set_font_size('10')   
        normal_right.set_border()
        #################################################################################
        normal_right_bold = workbook.add_format({'bold' :1, 'valign':'bottom','align':'right'})
        normal_right_bold.set_text_wrap()
        normal_right_bold.set_font_name('Arial')
        normal_right_bold.set_font_size('10')   
        normal_right_bold.set_border()                     
        #################################################################################
        normal_left_bold = workbook.add_format({'bold' :1, 'valign':'bottom','align':'left'})
        normal_left_bold.set_text_wrap()
        normal_left_bold.set_font_name('Arial')
        normal_left_bold.set_font_size('10')
        #################################################################################
        normal_left_border = workbook.add_format({'valign':'bottom','align':'left'})
        normal_left_border.set_text_wrap()
        normal_left_border.set_font_name('Arial')
        normal_left_border.set_font_size('10')
        normal_left_border.set_border()
        #################################################################################
        normal_center_border = workbook.add_format({'valign':'vcenter','align':'center'})
        normal_center_border.set_text_wrap()
        normal_center_border.set_font_name('Arial')
        normal_center_border.set_font_size('10')
        normal_center_border.set_border()
        #################################################################################
        normal_bold = workbook.add_format({'bold': 1,'valign':'vcenter','align':'center'})
        normal_bold.set_text_wrap()
        normal_bold.set_font_name('Arial')
        normal_bold.set_font_size('10')
        #################################################################################
        normal_bold_border = workbook.add_format({'bold': 1,'valign':'vcenter','align':'center'})
        normal_bold_border.set_text_wrap()
        normal_bold_border.set_font_name('Arial')
        normal_bold_border.set_font_size('10')
        normal_bold_border.set_border()
        #################################################################################
        merge_formats = workbook.add_format({'bold': 1,'align': 'center','valign': 'vcenter',})
        merge_formats.set_font_name('Arial')
        merge_formats.set_font_size('10')
        merge_formats.set_border()
        #################################################################################
        format_number_bold = workbook.add_format({'bold': 1,'valign':'vcenter','align':'right'})
        format_number_bold.set_num_format('#,##0.00')
        format_number_bold.set_font_name('Arial')
        format_number_bold.set_font_size('10')
        format_number_bold.set_border()
        #################################################################################
        format_number = workbook.add_format({'valign':'vcenter','align':'center'})
        format_number.set_num_format('#,##0.00')
        format_number.set_font_name('Arial')
        format_number.set_font_size('10')
        format_number.set_border()
        #################################################################################
        format_number_unborder = workbook.add_format({'valign':'vcenter','align':'right'})
        format_number_unborder.set_num_format('#,##0.00')
        format_number_unborder.set_font_name('Arial')
        format_number_unborder.set_font_size('10')        
        #################################################################################
        format_number_bold_minbord = workbook.add_format({'bold': 1,'valign':'vcenter','align':'right'})
        format_number_bold_minbord.set_num_format('#,##0.00')
        format_number_bold_minbord.set_font_name('Arial')
        format_number_bold_minbord.set_font_size('10')
        #################################################################################
        format_number_minbord = workbook.add_format({'valign':'vcenter','align':'right'})
        format_number_minbord.set_num_format('#,##0.00')
        format_number_minbord.set_font_name('Arial')
        format_number_minbord.set_font_size('10')
        #################################################################################
        format_number_total = workbook.add_format({'bold': 1,'valign':'vcenter','align':'center'})
        format_number_total.set_num_format('#,##0.00')
        format_number_total.set_font_name('Arial')
        format_number_total.set_font_size('10')
        format_number_total.set_border()        
             
        worksheet = workbook.add_worksheet("report")
        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 7)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 45)
        
        worksheet.merge_range('A1:G1', 'Daftar Penerima Consumer Pomo', center_title) #dynamic value for store name
        worksheet.write('A3','Brand', normal_left_unborder)
        worksheet.write('A4:A4','Nama BA', normal_left_unborder)
        worksheet.write('A5:A5','Bulan', normal_left_unborder)
        worksheet.write('B3', ': '+brand+'', normal_left_unborder)
        worksheet.write('B4', ': ', normal_left_unborder)
        worksheet.write('B5', ': '+month_check+ ' '+take_year+'', normal_left_unborder)
        
        worksheet.merge_range('A7:A8', 'DC', normal_bold_border)
        worksheet.merge_range('B7:B8', 'Store Name', normal_bold_border)
        worksheet.merge_range('C7:C8','Tanggal',normal_bold_border)
        worksheet.merge_range('D7:E7','Data Konsumen',normal_bold_border)
        worksheet.write('D8','Nama',normal_bold_border)
        worksheet.write('E8','No. HP',normal_bold_border)
        worksheet.merge_range('F7:F8','Nominal Pembelanjaan', normal_bold_border)
        worksheet.merge_range('G7:G8','Bentuk Consumer Promo', normal_bold_border)
        worksheet.freeze_panes(10,1)
        
        if filter_check == '1':
            print'all'
            self.env.cr.execute("""
                select temp.dc as dc, temp.shop as shop,temp.date as date, temp.name as name, temp.mobile as mobile,
                    sum(pline.price_subtotal_rel + (pline.price_subtotal_rel*0.1 )) as total_ppn, temp.product as product
                from
                    (
                    select 
                        to_char(date_order,'DD') as date, pline.order_id, spartner.name as name, porder.id,
                        spartner.mobile as mobile, pconfig.name as shop, dcpartner.name as dc, pproduct.name_template as product
                    from 
                        pos_order porder join pos_order_line pline on porder.id = pline.order_id
                        join res_partner spartner on porder.partner_id = spartner.id
                        join pos_session psession on porder.session_id = psession.id
                        join pos_config pconfig on psession.config_id = pconfig.id
                        join product_product pproduct on pproduct.id = pline.product_id
                        join stock_location slocation on slocation.id = pconfig.stock_location_id
                                join res_partner rpartner on rpartner.id = slocation.partner_id
                                join res_partner dcpartner on rpartner.dc_id = dcpartner.id 
                    where 
                        to_char(date_order,'MM') = %s  AND to_char(date_order,'YYYY') = %s and pline.discount=100 and pconfig.category_shop='shop_in_shop_mds'
                    ) as temp
                join 
                    pos_order_line pline on pline.order_id = temp.order_id
                where 
                    pline.order_id = temp.order_id
                group by
                    temp.product,
                    temp.dc,
                    temp.shop,
                    temp.date,
                    temp.mobile,
                    temp.name
                order by
                    temp.dc,
                    temp.shop
                    """, (take_month,take_year))
        else:
            print 'per brand'
            self.env.cr.execute("""
                select temp.dc as dc, temp.shop as shop,temp.date as date, temp.name as name, temp.mobile as mobile,
                    sum(pline.price_subtotal_rel + (pline.price_subtotal_rel*0.1 )) as total_ppn, temp.product as product
                from
                    (
                    select 
                        to_char(date_order,'DD') as date, pline.order_id, spartner.name as name, porder.id,
                        spartner.mobile as mobile, pconfig.name as shop, dcpartner.name as dc, pproduct.name_template as product
                    from 
                        pos_order porder join pos_order_line pline on porder.id = pline.order_id
                        join res_partner spartner on porder.partner_id = spartner.id
                        join pos_session psession on porder.session_id = psession.id
                        join pos_config pconfig on psession.config_id = pconfig.id
                        join product_product pproduct on pproduct.id = pline.product_id
                        join stock_location slocation on slocation.id = pconfig.stock_location_id
                                join res_partner rpartner on rpartner.id = slocation.partner_id
                                join res_partner dcpartner on rpartner.dc_id = dcpartner.id 
                    where 
                        to_char(date_order,'MM') = %s  AND to_char(date_order,'YYYY') = %s and pconfig.tags = %s and pline.discount=100 and pconfig.category_shop='shop_in_shop_mds'
                    ) as temp
                join 
                    pos_order_line pline on pline.order_id = temp.order_id
                where 
                    pline.order_id = temp.order_id
                group by
                    temp.product,
                    temp.dc,
                    temp.shop,
                    temp.date,
                    temp.mobile,
                    temp.name
                order by 
                    temp.dc
                    """, (take_month,take_year,brand_id))
            
        form_obj=self.env.cr.fetchall()
        print form_obj
        
        row = 0
        inc= 0
        dc=0
        number = 1
        store = 0
        for pos in form_obj:
            print pos[0]
            print pos[1]
            print'==============='
            print len(form_obj)
            print inc
            print '============='
            worksheet.write(row+8, 0, pos[0], normal_center_border)
            worksheet.write(row+8, 1, pos[1], normal_center_border)
            worksheet.write(row+8, 2, pos[2], normal_center_border)
            worksheet.write(row+8, 3, pos[3], normal_left_border)
            worksheet.write(row+8, 4, pos[4], normal_right)
            worksheet.write(row+8, 5, pos[5], normal_center_border)
            worksheet.write(row+8, 6, pos[6], normal_left_border)
            number +=1
            row += 1
            if len(form_obj)-1==inc or pos[0]!=form_obj[inc+1][0]:
                if dc==0:
                    print'111'
                    string_dc = 'A9:A'+str(row+8)
                else :
                    print'222'
                    string_dc = 'A'+str(((row+8)-number)+2)+':A'+str((row+9)-1)
                print'--------------------------'
                print'dc', dc
                print'string dc',string_dc
                print'--------------------------'
                dc += 1
                worksheet.merge_range(string_dc, pos[0], normal_center_border)
                
            if len(form_obj)-1==inc or pos[1]!=form_obj[inc+1][1]:
                if store==0:
                    print '111111'
                    string_store = 'B9:B'+str(row+8)
                else :
                    print '22222'
                    string_store = 'B'+str(((row+8)-number)+2)+':B'+str((row+9)-1)
                print'++++++++++++++++++++++++++++++++'
                print 'number',number
                print 'store',store
                print 'string_store',string_store
                print '+++++++++++++++++++++++++++++++'
                store += 1
                number = 1
                worksheet.merge_range(string_store, pos[1], normal_center_border)
            
            inc += 1
            
            
        workbook.close()
        
        out = base64.encodestring(bz.getvalue())
        self.write({'state_x':'get', 'data_x':out, 'name': filename})

        ir_model_data = self.env['ir.model.data']
        bz.close()
        form_res = ir_model_data.get_object_reference('pti_mds_consumer_promo', 'consumer_promo_mds_nasional_view')
        form_id = form_res and form_res[1] or False
        
        return {
            'name': ('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'consumer.promo.nasional.wizard',
            'res_id': self.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }
