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
    _name = "consumer.promo.store.wizard"

    store = fields.Many2one('pos.config', string="Store") 
    end_period = fields.Date(string="End Period")
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    Date = fields.Date('Date') 

    @api.multi
    def generate_excel_consumer_store(self):
        bz = StringIO()
        workbook =  xlsxwriter.Workbook(bz)
        
        date = datetime.strptime(self.Date,'%Y-%m-%d')    #date still integer
        take_year = datetime.strftime(date,'%Y')          #date change to string
        take_month= datetime.strftime(date,'%m')
        year = date.year
        month = date.month
        
        print'integer',month , year
        print'str',take_month , take_year
        
#         if year < 10:
#             month_str = '0'+take_month+''
#         else:
#             month_str = take_month
#         print '=======',take_month,month_str
        
        store_name = self.store.name
        store_id = self.store.id
        print store_id,store_name
        month_dict = {  
                        1 : 'January',2:'February',3:'March',4:'April',5:'May',6:'June',
                        7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'
                     }
        
        
        month_check = month_dict[month]
        
        filename = 'Laporan Consumer Promo Store : '+store_name+', Bulan : '+month_check+'.xlsx'

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
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 45)
        
        worksheet.merge_range('A1:E1', 'Daftar Penerima Consumer Pomo', center_title) #dynamic value for store name
        worksheet.merge_range('A3:B3','Store Name', normal_left_unborder)
        worksheet.merge_range('A4:B4','Nama BA', normal_left_unborder)
        worksheet.merge_range('A5:B5','Bulan', normal_left_unborder)
        worksheet.merge_range('C3:E3', ': '+store_name+'', normal_left_unborder)
        worksheet.write('C4', ': ', normal_left_unborder)
        worksheet.write('C5', ': '+month_check+ ' '+take_year+'', normal_left_unborder)
        
        worksheet.merge_range('A7:A8','Tanggal',normal_bold_border)
        worksheet.merge_range('B7:C7','Data Konsumen',normal_bold_border)
        worksheet.write('B8','Nama',normal_bold_border)
        worksheet.write('C8','No. HP',normal_bold_border)
        worksheet.merge_range('D7:D8','Nominal Pembelanjaan', normal_bold_border)
        worksheet.merge_range('E7:E8','Bentuk Consumer Promo', normal_bold_border)
        worksheet.freeze_panes(10,2)
        
        
                    
        self.env.cr.execute("""
               select temp.date as date, temp.name as name, temp.mobile as mobile,
                    sum(pline.price_subtotal_rel + (pline.price_subtotal_rel*0.1 )) as total_ppn,
                    temp.product as product
               from
                    (
                    select 
                        to_char(date_order,'DD') as date, pline.order_id, spartner.name as name,pline.discount, porder.id,
                        spartner.mobile as mobile, pconfig.name as shop, pproduct.name_template as product
                    from 
                        pos_order porder join pos_order_line pline on porder.id = pline.order_id
                        join res_partner spartner on porder.partner_id = spartner.id
                        join pos_session psession on porder.session_id = psession.id
                        join pos_config pconfig on psession.config_id = pconfig.id
                        join product_product pproduct on pproduct.id = pline.product_id
                    where 
                        to_char(date_order,'MM') = %s AND to_char(date_order,'YYYY') = %s and pconfig.id =%s and pline.discount=100 and pconfig.category_shop='shop_in_shop_mds'
                    ) as temp
                join 
                    pos_order_line pline on pline.order_id = temp.order_id
                where 
                    pline.order_id = temp.order_id
                group by
                    temp.date,
                    temp.product,
                    temp.name,
                    temp.mobile
                order by
                    temp.date
                """, (take_month,take_year,store_id))
        form_obj=self.env.cr.fetchall()
        print form_obj
        
        row = 0
        for pos in form_obj:
            worksheet.write(row+8, 0, pos[0], normal_center_border)
            worksheet.write(row+8, 1, pos[1], normal_left_border)
            worksheet.write(row+8, 2, pos[2], normal_center_border)
            worksheet.write(row+8, 3, pos[3], normal_right)
            worksheet.write(row+8, 4, pos[4], normal_left_border)
            row += 1
        workbook.close()
        
        out = base64.encodestring(bz.getvalue())
        self.write({'state_x':'get', 'data_x':out, 'name': filename})

        ir_model_data = self.env['ir.model.data']
        bz.close()
        form_res = ir_model_data.get_object_reference('pti_mds_consumer_promo', 'consumer_promo_mds_store_view')
        form_id = form_res and form_res[1] or False
        
        return {
            'name': ('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'consumer.promo.store.wizard',
            'res_id': self.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }
