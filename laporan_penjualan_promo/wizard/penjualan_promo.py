from openerp import models, fields, api
from cStringIO import StringIO
from datetime import datetime, timedelta
import xlsxwriter
import base64
import time
from jinja2.runtime import to_string

    
class LaporanPromoReportWizard(models.TransientModel):
    _name = "laporan.promo.report.wizard"
    
    filter = fields.Selection((('1','All'),('2', 'Brand')), string='Filter', default='1')
    brand_id = fields.Many2one('product.brand','Brand')
    start_period = fields.Date(string="Start Period")
    end_period = fields.Date(string="End Period")
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    check_all=fields.Boolean('Check')

    @api.multi
    def generate_excel(self):
        form_bc_obj = self.env['pos.order']
        for this in self:
            start_period = this.start_period
            end_period = this.end_period
            today = datetime.now()
            sp=datetime.strptime(start_period, '%Y-%m-%d')
            ep=datetime.strptime(end_period, '%Y-%m-%d')
#             spq=datetime.strptime(start_period, '%d-%m-%Y')
#             epq=datetime.strptime(end_period, '%d-%m-%Y')
            
            bz = StringIO()
            workbook = xlsxwriter.Workbook(bz)
            

            filename = 'Laporan Penjualan Promo Per Store MDS (Nasional).xls'


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
            normal_left_bold = workbook.add_format({'bold' :1, 'valign':'bottom','align':'left'})
            normal_left_bold.set_font_name('Arial')
            normal_left_bold.set_font_size('10')
            #################################################################################
            normal_left_border = workbook.add_format({'valign':'bottom','align':'left'})
            normal_left_border.set_text_wrap()
            normal_left_border.set_font_name('Arial')
            normal_left_border.set_font_size('10')
            normal_left_border.set_border()
            #################################################################################
            normal_right_border = workbook.add_format({'valign':'bottom','align':'right'})
            normal_right_border.set_text_wrap()
            normal_right_border.set_font_name('Arial')
            normal_right_border.set_font_size('10')
            normal_right_border.set_border()
            #################################################################################
            normal_center_border = workbook.add_format({'valign':'left','align':'center'})
            normal_center_border.set_text_wrap()
            normal_center_border.set_font_name('Arial')
            normal_center_border.set_font_size('10')
            normal_center_border.set_border()
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
            normal_bold_border = workbook.add_format({'bold': 1,'valign':'vcenter','align':'center'})
            normal_bold_border.set_text_wrap()
            normal_bold_border.set_font_name('Arial')
            normal_bold_border.set_font_size('10')
            normal_bold_border.set_border()
            #################################################################################
            normal_border = workbook.add_format({'valign':'vcenter','align':'left'})
            normal_border.set_text_wrap()
            normal_border.set_font_name('Arial')
            normal_border.set_font_size('10')
            normal_border.set_border()
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
            format_number = workbook.add_format({'valign':'vcenter','align':'right'})
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
            format_number_bold_unborder = workbook.add_format({'bold': 1,'valign':'vcenter','align':'right'})
            format_number_bold_unborder.set_num_format('#,##0.00')
            format_number_bold_unborder.set_font_name('Arial')
            format_number_bold_unborder.set_font_size('10')

            
            worksheet = workbook.add_worksheet("Laporan Penj. Promo per store")
            worksheet.set_column('A:A', 15)
            worksheet.set_column('B:B', 25)
            worksheet.set_column('C:C', 25)
            worksheet.set_column('D:D', 55)
            worksheet.set_column('E:E', 12)
            worksheet.set_column('F:F', 10)
            worksheet.set_column('G:G', 6)
            worksheet.set_column('H:H', 6)
            worksheet.set_column('I:I', 14)
            worksheet.set_column('J:J', 16)
            worksheet.set_column('K:K', 14)
            
            worksheet.write('A1', 'Laporan Penjualan Promo', normal_left_bold)
            worksheet.write('A3','Start Period :',normal_left_bold)
            worksheet.write('A4', sp.strftime('%d %b %Y'),normal_left)
            worksheet.write('C3', 'End Period :',normal_left_bold)
            worksheet.write('C4', ep.strftime('%d %b %Y'),normal_left) 
            worksheet.merge_range('E3:F3', 'Print Date :',normal_left_bold)
            worksheet.merge_range('E4:F4', today.strftime('%d %b %Y %H:%M'),normal_left) 
            
            worksheet.merge_range('A5:A6', 'DC', normal_bold_border)
            worksheet.merge_range('B5:B6', 'Store Name', normal_bold_border)
            worksheet.merge_range('C5:C6', 'Period Promo', normal_bold_border)
            worksheet.merge_range('D5:D6', 'Product', normal_bold_border)
            worksheet.merge_range('E5:E6', 'SKU', normal_bold_border)
            worksheet.merge_range('F5:F6', 'Price', normal_bold_border)
            worksheet.merge_range('G5:G6', 'Qty', normal_bold_border)
            worksheet.merge_range('H5:I5', 'Disc.', normal_bold_border)
            worksheet.write('H6', '%', normal_bold_border)
            worksheet.write('I6', 'Rp', normal_bold_border)
            worksheet.merge_range('J5:J6', 'Total', normal_bold_border)
            worksheet.merge_range('K5:K6', 'Ppn', normal_bold_border)
            worksheet.freeze_panes(6,0)
            
            self.env.cr.execute("""
                select 
                    dcpartner.name as dc, pconfig.name as Store, 
                    to_char(ppricelistitem.date_start,'DD Mon YYYY')|| ' - ' ||to_char(ppricelistitem.date_end, 'DD Mon YYYY') period,
                    pproduct.name_template as Product, porder.shop_identifier_period as sku_period, porder.shop_identifier_origin as sku_origin,
                    pline.price_unit as Price, sum(pline.qty) as Qty, ppricelistitem.price_discount,
                    round((pline.price_unit*sum(pline.qty))*(ppricelistitem.price_discount/100),2) as Rp,
                    round((pline.price_unit*sum(pline.qty)-((pline.price_unit*sum(pline.qty))*(ppricelistitem.price_discount/100))),2) as Total,
                    round((pline.price_unit*sum(pline.qty)-((pline.price_unit*sum(pline.qty))*(ppricelistitem.price_discount/100)))*0.1,2) as Ppn
                from 
                    pos_order as porder 
                join 
                    pos_order_line as pline on porder.id = pline.order_id 
                join 
                    product_pricelist as ppricelist on porder.pricelist_id = ppricelist.id
                join 
                    product_pricelist_item as ppricelistitem on ppricelist.id = ppricelistitem.pricelist_id
                join 
                    product_template as ptemplate on ppricelistitem.product_tmpl_id = ptemplate.id
                join 
                    product_product as pproduct on pproduct.id = pline.product_id
                join 
                    pos_session as psession on porder.session_id = psession.id
                join 
                    pos_config as pconfig on psession.config_id = pconfig.id
                join 
                    stock_location slocation on slocation.id = pconfig.stock_location_id
                join 
                    res_partner rpartner on rpartner.id = slocation.partner_id
                join 
                    res_partner dcpartner on rpartner.dc_id = dcpartner.id 
                where 
                    ppricelistitem.date_start >= %s AND ppricelistitem.date_end <= %s and pconfig.category_shop = 'shop_in_shop_mds'
                group by
                    dcpartner.name, pconfig.name,
                    pproduct.name_template, ppricelistitem.date_start,
                    ppricelistitem.date_end, pproduct.name_template, 
                    porder.shop_identifier_period, porder.shop_identifier_origin,
                    pline.price_unit, ppricelistitem.price_discount
                order by pconfig.name
                """, (start_period+' 00:00:00', end_period+' 23:59:59'))
            
            
            obj_pos = self.env.cr.fetchall()

            row=1
            number=1
            inc = 0
            sum_total    = 0.0
            sum_ppn      = 0.0
            sum_disc = 0.0
            sum_all_disc = 0.0
            sum_qt = 0.0
            sum_all_ppn  = 0.0
            total_all_sales  = 0.0 
            sum_all_disc = 0.0
            total_all_sales = 0.0
            sku_list = {}
            iniSN = 0
            iniDC = 0
            stringSN = ''
            stringDC = ''
            numberDC=1
            

            for pos in obj_pos:
                worksheet.write(row+5, 2, pos[2], normal_left_border)
                worksheet.write(row+5, 3, pos[3], normal_left_border)
                sku = pos[5]
                if pos[4]:
                    sku = pos[4]  
                worksheet.write(row+5, 4, sku, normal_center_border)
                worksheet.write(row+5, 5, pos[6], format_number)
                worksheet.write(row+5, 6, pos[7], format_number)
                worksheet.write(row+5, 7, pos[8], format_number)
                worksheet.write(row+5, 8, pos[9], format_number)
                worksheet.write(row+5, 9, pos[10], format_number)
                worksheet.write(row+5, 10, pos[11], format_number)
                
                sku_list.update({ inc : [sku,pos[10]]})  
                sum_disc += pos[9]
                sum_total += pos[10]
                sum_ppn += pos[11]
                sum_all_ppn += pos[11]
                sum_all_disc += pos[9]
                number += 1
                numberDC += 1
                sum_qt += pos[7]
                row +=1
                
                if len(obj_pos)-1==inc or pos[0]!=obj_pos[inc+1][0]:
                    if iniDC==0:
                        stringDC = 'A7:A'+to_string(row+6)
                    else :
                        stringDC = 'A'+to_string(((row+6)-number)+1)+':A'+to_string(row+6)
                    iniDC += 1
                    numberDC = 1
                    worksheet.merge_range(stringDC, pos[0], normal_border) 
                    
                if len(obj_pos)-1==inc or pos[1]!=obj_pos[inc+1][1]:
                    worksheet.write(row+5 , 0, '', normal_left_border)
                    worksheet.write(row+5 , 1, '', normal_left_border)
                    worksheet.write(row+5 , 2, '', normal_left_border)
                    worksheet.write(row+5 , 3, '', normal_left_border)
                    worksheet.write(row+5 , 4, '', normal_left_border)
                    worksheet.write(row+5 , 5, '', normal_left_border)
                    worksheet.write(row+5 , 6, '', normal_left_border)
                    worksheet.write(row+5 , 7, '', format_number_bold)        
                    worksheet.write(row+5 , 8, sum_disc, format_number_bold)        
                    worksheet.write(row+5 , 9, sum_total, format_number_bold)  
                    worksheet.write(row+5 , 10, sum_ppn, format_number_bold)
                    sum_disc = 0.0
                    sum_total    = 0.0
                    sum_ppn      = 0.0
                    
                    if iniSN==0:
                        stringSN = 'B7:B'+to_string(row+5)
                    else :
                        stringSN = 'B'+to_string(((row+6)-number)+1)+':B'+to_string(row+5)
                    iniSN += 1
                    number = 1
                    row = row+1
                    worksheet.merge_range(stringSN, pos[1], normal_border) 
                inc += 1
                     
            sku_set = []
            for sku in sku_list.values():
                sku_set.append(sku[0])
    
            sku_set = list(set(sku_set))
            sku_values = dict()
            for  sku_set in sku_set:
                sku_total=0            
                for sku in sku_list.values():               
                    if sku_set == sku[0]:
                        sku_total += sku[1]                
                sku_values.update({sku_set : sku_total})    
    
            
            worksheet.write(row+7 , 1, 'Taxes (Rp)', normal_left_bold)     
            worksheet.write(row+8 , 1, 'PPN 10%', normal_left)
            worksheet.write(row+8 , 9, sum_all_ppn, format_number_unborder)                            
            worksheet.write(row+9 , 1, 'Sales by SKU', normal_left_bold)
            for key, value in sku_values.iteritems():
                row += 1
                worksheet.write(row+9, 1, key, normal_left)
                worksheet.write(row+9, 9, value, format_number_unborder)            
                total_all_sales += value
            worksheet.write(row+10 , 1, 'Total Sales (Rp)', normal_left_bold)                        
            worksheet.write(row+10 , 9, total_all_sales, format_number_bold_unborder)     
            worksheet.write(row+11 , 1, 'Qty of Product (Pcs)', normal_left_bold)                        
            worksheet.write(row+11 , 9, sum_qt, format_number_unborder) 
            worksheet.write(row+12 , 1, 'Total Discount (Rp)', normal_left_bold)                        
            worksheet.write(row+12 , 9, sum_all_disc, format_number_bold_unborder) 
            workbook.close()

            out = base64.encodestring(bz.getvalue())
            this.write({'state_x':'get', 'data_x':out, 'name': filename})

            ir_model_data = self.env['ir.model.data']
            bz.close()
            form_res = ir_model_data.get_object_reference('laporan_penjualan_promo', 'laporan_promo_report_wizard_view')
            form_id = form_res and form_res[1] or False
            
            return {
                'name': ('Download XLS'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'laporan.promo.report.wizard',
                'res_id': this.id,
                'view_id': False,
                'views': [(form_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current'
            }

