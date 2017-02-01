from openerp import models, fields, api
from cStringIO import StringIO
from datetime import datetime, timedelta
import xlsxwriter
import base64
import time
from jinja2.runtime import to_string
from gdata.contentforshopping.data import Domain

  
class IndependentNasionalStoreProdukreport(models.TransientModel):
    _name = "independent.nasional.store.report.produk.wizard"
    
    start_period = fields.Date(string="Start Period")
    end_period = fields.Date(string="End Period")
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    check_all=fields.Boolean('Check')
    
    @api.multi
    def generate_excel_produk(self):
        form_bc_obj = self.env['pos.order.line']

        start_period = self.start_period
        end_period = self.end_period
        today = datetime.now()
        sp=datetime.strptime(start_period, '%Y-%m-%d')
        ep=datetime.strptime(end_period, '%Y-%m-%d')
        
        bz = StringIO()
        workbook = xlsxwriter.Workbook(bz)

        filename = 'Produk.xlsx'

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
        normal_left.set_border()
        #################################################################################
        normal_left_unborder = workbook.add_format({'valign':'bottom','align':'left'})
        normal_left_unborder.set_text_wrap()
        normal_left_unborder.set_font_name('Arial')
        normal_left_unborder.set_font_size('10')        
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
        normal_center_border = workbook.add_format({'valign':'bottom','align':'center'})
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
        normal_border = workbook.add_format({'valign':'vcenter','align':'left'})
        normal_border.set_text_wrap()
        normal_border.set_font_name('Arial')
        normal_border.set_font_size('10')
        normal_border.set_border()
        
    
        worksheet = workbook.add_worksheet("report")
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 60)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 5)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        
        worksheet.merge_range('A1:J1', 'PRODUK', normal_center_border)
        worksheet.write('B3','Start Period :', normal_left_unborder)
        worksheet.write('B4', sp.strftime('%d %b %Y'), normal_left_unborder)
        worksheet.write('D3', 'End Period :', normal_left_unborder)
        worksheet.write('D4', ep.strftime('%d %b %Y'),normal_left_unborder) 
        worksheet.write('F3', 'Print Date :', normal_left_unborder)
        worksheet.write('F4', today.strftime('%d %b %Y %H:%M'), normal_left_unborder) 
        
        worksheet.merge_range('A6:A7', 'No.', normal_bold_border)
        worksheet.merge_range('B6:B7', 'Product',normal_bold_border)
        worksheet.merge_range('C6:C7', 'Price', normal_bold_border)
        worksheet.merge_range('D6:D7', 'Qty',normal_bold_border)
        worksheet.merge_range('E6:F6', 'Discount', normal_bold_border)
        worksheet.write('E7','%', normal_bold_border)
        worksheet.write('F7','Rp', normal_bold_border)
        worksheet.merge_range('G6:G7', 'Total', normal_bold_border)
        worksheet.merge_range('H6:H7', 'Ppn', normal_bold_border)
        worksheet.freeze_panes(7,3)
        

        self.env.cr.execute("""
            select pconfig.name as shop, pproduct.name_template as product,  
                     pline.price_unit as price, sum(pline.qty) as qty, pline.discount as discount, pline.price_unit*sum(pline.qty)*pline.discount/100 as total_disc, 
                     sum(pline.price_subtotal_rel) as total, sum(pline.price_subtotal_rel) * 0.1 as ppn , pproduct.voucher as voucher
                         from pos_order porder 
                         join pos_order_line pline on porder.id = pline.order_id 
                         join pos_session psession on porder.session_id = psession.id
                         join pos_config pconfig on psession.config_id = pconfig.id
                         join product_product pproduct on pproduct.id = pline.product_id
                         join product_template ptemplate on ptemplate.id = pproduct.product_tmpl_id
                         join product_category_product_template_rel prel on prel.product_template_id = ptemplate.id
                         join product_category pcategory on pcategory.id = prel.product_category_id                     
                     where pcategory.parent_id = (select id from product_category where name = %s) 
                     AND porder.date_order >=%s 
                     AND porder.date_order <=%s 
                     AND pconfig.category_shop = 'stand_alone'
                     AND pconfig.stand_alone_categ = 'independent' 
                     AND (pproduct.voucher = 'false' or pproduct.voucher is null) 
                     group by pconfig.name, pproduct.name_template,
                                                   psession.shop_identifier_origin, 
                                                   psession.shop_identifier_period,
                                                   pline.price_unit, pline.price_unit, pline.discount,pproduct.voucher
                                            order by pconfig.name   
                """, ('WBH', start_period+' 00:00:00', end_period+' 23:59:59'))
        obj_pos = self.env.cr.fetchall()                         
        
        row = 0
        number = 1
        inc = 0
        sum_total    = 0.0
        sum_ppn      = 0.0
        sum_discount = 0.0
        sum_all_discount = 0.0
        sum_cash = 0.0
        sum_all_ppn  = 0.0
        total_all_sales  = 0.0 
        qty_voucher = 0.0
        sum_voucher = 0.0
        sum_total_voucher = 0.0
        sum_uang_total=0.0
        iniSN = 0.0
        
        self.env.cr.execute("""
            select pconfig.name as shop, paccount.balance_start as balance
                      from pos_order porder join pos_order_line pline on porder.id = pline.order_id 
                      join pos_session psession on porder.session_id = psession.id
                      join pos_config pconfig on psession.config_id = pconfig.id
                      join account_bank_statement paccount on psession.id = paccount.pos_session_id
                  where porder.date_order >=%s AND porder.date_order <=%s AND pconfig.category_shop = 'stand_alone' AND pconfig.stand_alone_categ = 'independent' 
                  group by pconfig.name,paccount.balance_start
                                         order by pconfig.name
                    """, (start_period+' 00:00:00', end_period+' 23:59:59'))
        obj_pos_cash = self.env.cr.fetchall()                 
        for cash in obj_pos_cash:
            sum_cash      += cash[1]        
        sku_list = {}
        for pos in obj_pos:
            worksheet.write(row+7 , 0, number, normal_center)
            worksheet.write(row+7 , 1, pos[1], normal_left)                        
            
            worksheet.write(row+7 , 2, pos[2], format_number)
            worksheet.write(row+7 , 3, pos[3], normal_center)            
            if pos[4]==0:
                worksheet.write(row+7 , 4, '', normal_center)
                worksheet.write(row+7 , 5, '', format_number)        
            else:
                worksheet.write(row+7 , 4, pos[4], normal_center)
                worksheet.write(row+7 , 5, pos[5], format_number)                                    
                sum_discount += pos[5]
            worksheet.write(row+7 , 6, pos[6], format_number)  
            worksheet.write(row+7 , 7, pos[7], format_number)
            self.env.cr.execute("""
                select pconfig.name as shop, pproduct.name_template as product,  
                      pline.price_unit as price, sum(pline.qty) as qty, 
                      sum(pline.price_subtotal_rel) as total, 
                      pproduct.voucher as voucher, 
                      paccount.balance_start as balance
                          from pos_order porder join pos_order_line pline on porder.id = pline.order_id 
                          join pos_session psession on porder.session_id = psession.id
                          join pos_config pconfig on psession.config_id = pconfig.id
                          join product_product pproduct on pproduct.id = pline.product_id
                          join account_bank_statement paccount on psession.id = paccount.pos_session_id
                      where porder.date_order >=%s AND porder.date_order <=%s AND pconfig.category_shop = 'stand_alone' AND pproduct.voucher = 'true' AND pconfig.stand_alone_categ = 'independent' 
                      group by pconfig.name, pproduct.name_template, paccount.balance_start,
                                                    psession.shop_identifier_origin, 
                                                    psession.shop_identifier_period,
                                                    pline.price_unit, pline.price_unit,pproduct.voucher,paccount.balance_start
                                             order by pconfig.name
                        """, (start_period+' 00:00:00', end_period+' 23:59:59'))
            obj_pos_voucher = self.env.cr.fetchall()
        
            for voucher in obj_pos_voucher:
                worksheet.write(row+9 , 1, voucher[1], normal_left)
                worksheet.write(row+9 , 2, voucher[2], format_number)
                worksheet.write(row+9 , 3, voucher[3], normal_center)
                worksheet.write(row+9 , 4, '', normal_center)
                worksheet.write(row+9 , 5, '', normal_center)
                worksheet.write(row+9 , 6, voucher[4], format_number_bold)
                worksheet.write(row+9 , 7, '', format_number_bold)

            sum_total    += pos[6]
            sum_ppn      += pos[7]
                        
            number += 1
            row += 1                              
            
            if len(obj_pos)-1==inc or pos[0]!=obj_pos[inc+1][0]:
                worksheet.merge_range('A'+str(row+8)+':'+'F'+str(row+8), 'Total Penjualan(Rp)', normal_bold_border)
                worksheet.write(row+7 , 4, '', normal_center)
                worksheet.write(row+7 , 5, '', normal_center)
                worksheet.write(row+7 , 6, '', format_number_bold)        
                worksheet.write(row+7 , 7, '', format_number_bold)        
                worksheet.write(row+7 , 6, sum_total, format_number_bold)  
                worksheet.write(row+7 , 7, sum_ppn, format_number_bold)
                worksheet.write(row+9 , 1, 'Modal Kembalian', normal_left)
                worksheet.write(row+9 , 6, (sum_cash*-1), format_number_bold)
                worksheet.write(row+9 , 7, '', format_number_bold)
                worksheet.merge_range('A'+str(row+11)+':'+'F'+str(row+11), 'Total Uang Disetor', normal_bold_border)
                sum_uang = (sum_total+voucher[4]+(sum_cash*-1))
                worksheet.write(row+10 , 6, sum_uang, format_number_bold)
                worksheet.write(row+10 , 7, sum_ppn, format_number_bold)
                sum_all_ppn  += sum_ppn  
                total_all_sales += sum_total                                             
                sum_all_discount += sum_discount 
                sum_total_voucher+= voucher[4]
                sum_uang_total += sum_uang
                sum_total    = 0.0
                sum_ppn      = 0.0                
                row +=4
                number = 1
                
            inc += 1
#         print 'panjaaang' , len(pos[0])    
        worksheet.write(row+10 , 1, 'Taxes (Rp)', normal_left_bold)     
        worksheet.write(row+11 , 1, 'PPN 10%', normal_left_unborder)
        worksheet.write(row+11 , 6, sum_all_ppn, format_number_unborder)                            

        worksheet.write(row+12 , 1, 'Total Sales (Rp)', normal_left_bold)                        
        worksheet.write(row+12 , 6, total_all_sales, format_number_bold_minbord)                                    
        
        worksheet.write(row+13 , 1, 'Total Discount (Rp)', normal_left_bold)                        
        worksheet.write(row+13 , 6, sum_all_discount, format_number_bold_minbord)
                                            
        worksheet.write(row+14 , 1, 'Total Voucher (Rp)', normal_left_bold)                        
        worksheet.write(row+14 , 6, abs(sum_total_voucher), format_number_bold_minbord)                                    

        worksheet.write(row+14 , 1, 'Total Uang Disetor (Rp)', normal_left_bold)                        
        worksheet.write(row+14 , 6, abs(sum_uang_total), format_number_bold_minbord)                                            
        workbook.close()

        out = base64.encodestring(bz.getvalue())
        self.write({'state_x':'get', 'data_x':out, 'name': filename})

        ir_model_data = self.env['ir.model.data']
        bz.close()
        form_res = ir_model_data.get_object_reference('pti_pos_independent_nasional_report', 'independent_nasional_store_report_produk_wizard_view')
        form_id = form_res and form_res[1] or False
        
        return {
            'name': ('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'independent.nasional.store.report.produk.wizard',
            'res_id': self.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }


