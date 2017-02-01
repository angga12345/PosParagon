from openerp import models, fields, api
from cStringIO import StringIO
from datetime import datetime, timedelta
import xlsxwriter
import base64
import time


    
class LaporanPromoDiscountReportWizard(models.TransientModel):
    _name = "laporan.promo.discount.report.wizard"

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
            
            bz = StringIO()
            workbook = xlsxwriter.Workbook(bz)

            filename = 'Laporan Penjualan Promo Discount WBH Nasional.xls'

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
            normal_left_border = workbook.add_format({'valign':'vcenter','align':'left'})
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
            normal_center_border = workbook.add_format({'valign':'vcenter','align':'center'})
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

            
            worksheet = workbook.add_worksheet("Laporan Penj. Promo Discount")
            worksheet.set_column('A:A', 20)
            worksheet.set_column('B:B', 20)
            worksheet.set_column('C:C', 20)
            worksheet.set_column('D:D', 55)
            worksheet.set_column('E:E', 10)
            worksheet.set_column('F:F', 4)
            worksheet.set_column('G:G', 4)
            worksheet.set_column('H:H', 15)
            worksheet.set_column('I:I', 15)
            worksheet.set_column('J:J', 15)
            
            worksheet.merge_range('A1:J1', 'Laporan Penjualan Promo Discount', center_title)
            worksheet.write('A3','Start Period :',normal_left_bold)
            worksheet.write('A4', sp.strftime('%d %b %Y'),normal_left_bold)
            worksheet.write('C3', 'End Period :',normal_left_bold)
            worksheet.write('C4', ep.strftime('%d %b %Y'),normal_left_bold) 
            worksheet.write('E3', 'Print Date :',normal_left_bold)
            worksheet.write('E4', today.strftime('%d %b %Y %H:%M'),normal_left_bold) 
            
            worksheet.merge_range('A5:A6', 'DC', normal_bold_border)
            worksheet.merge_range('B5:B6', 'Store Name', normal_bold_border)
            worksheet.merge_range('C5:C6', 'Period Promo', normal_bold_border)
            worksheet.merge_range('D5:D6', 'Product', normal_bold_border)
            worksheet.merge_range('E5:E6', 'Price', normal_bold_border)
            worksheet.merge_range('F5:F6', 'Qty', normal_bold_border)
            worksheet.merge_range('G5:H5', 'Disc.', normal_bold_border)
            worksheet.write('G6', '%', normal_bold_border)
            worksheet.write('H6', 'Rp', normal_bold_border)
            worksheet.merge_range('I5:I6', 'Total', normal_bold_border)
            worksheet.merge_range('J5:J6', 'Ppn', normal_bold_border)
            
            worksheet.freeze_panes(6,2)
            
            self.env.cr.execute("""
                SELECT
                    x.name, x.date,x.duration,x.product,x.price,x.qty,x.discount,x.type
                FROM(
                    select pconfig.name as name,lprogram.start_date as date, to_char(lprogram.start_date,'DD')|| ' - ' ||to_char(lprogram.end_date, 'DD Mon YYYY') as duration, pproduct.name_template as product,pline.price_unit as price, sum(pline.qty) as qty,  pline.discount as discount,ptemplate.type
                    from pos_order_line pline join pos_order porder on porder.id = pline.order_id 
                        join loyalty_reward lreward on lreward.id = porder.loyalty_reward_id
                        join loyalty_program lprogram on lprogram.id = lreward.loyalty_program_id
                        join product_product pproduct on pproduct.id = pline.product_id
                        join pos_session psession on psession.id = porder.session_id
                        join pos_config pconfig on pconfig.id = psession.config_id
                        join product_template ptemplate on ptemplate.id = pproduct.product_tmpl_id
                    where
                        lprogram.start_date >= %s
                        AND lprogram.end_date <= %s
                        and pline.discount > 0
                    group by pconfig.name, pline.discount, pline.price_unit, lprogram.start_date, lprogram.end_date, pproduct.name_template,ptemplate.type
                    UNION
                    select pconfig.name as name,lprogram.start_date as date, to_char(lprogram.start_date,'DD')|| ' - ' ||to_char(lprogram.end_date, 'DD Mon YYYY') as duration, lreward.name as product ,porder.special_price as price, count(porder.id) as qty,  0 as discount, '' as type
                    from pos_order porder 
                        join loyalty_reward lreward on lreward.id = porder.loyalty_reward_id
                        join loyalty_program lprogram on lprogram.id = lreward.loyalty_program_id
                        join pos_session psession on psession.id = porder.session_id
                        join pos_config pconfig on pconfig.id = psession.config_id
                    where
                        lprogram.start_date >= %s
                        AND lprogram.end_date <= %s
                        and porder.special_price > 0
                    group by pconfig.name, lprogram.start_date, lprogram.end_date, lreward.name,porder.special_price
                    UNION
                    select pconfig.name as name,lprogram.start_date as date, to_char(lprogram.start_date,'DD')|| ' - ' ||to_char(lprogram.end_date, 'DD Mon YYYY') as duration, lreward.name as product ,porder.max_reward_value as price, count(porder.id) as qty,  0 as discount, '' as type
                    from pos_order porder 
                        join loyalty_reward lreward on lreward.id = porder.loyalty_reward_id
                        join loyalty_program lprogram on lprogram.id = lreward.loyalty_program_id
                        join pos_session psession on psession.id = porder.session_id
                        join pos_config pconfig on pconfig.id = psession.config_id
                    where
                        lprogram.start_date >= %s
                        AND lprogram.end_date <= %s
                        and porder.max_reward_value > 0
                    group by pconfig.name, lprogram.start_date, lprogram.end_date, lreward.name,porder.max_reward_value
                    ) 
                    as x
                order by 1,2,4
                """, (start_period+' 00:00:00', end_period+' 23:59:59',start_period+' 00:00:00', end_period+' 23:59:59',start_period+' 00:00:00', end_period+' 23:59:59'))
            obj_pos = self.env.cr.fetchall()
            
            
            temp_vendor = False
            row = 1
            sum_rp = sum_total = sum_ppn = total_ppn = total_discount = total_sales = serv = count_of_sum = prod = 0
            start_merge = row + 6
            count_vend = -1
            for pos in obj_pos:
                
                if temp_vendor == False:
                    temp_vendor = pos[0]
                
                if pos[6] == 0:
                    discount = 0
                    amount_total = (pos[5] * pos[4] - discount) * -1
                    taxed = 0
                else:
                    discount = (pos[5] * pos[4]) * (pos[6] / 100)
                    amount_total = pos[5] * pos[4] - discount
                    taxed = amount_total * 0.1

                if(temp_vendor != pos[0] or (len(obj_pos) == 1 and len(obj_pos) != count_of_sum+1)):
                    if (start_merge + count_vend) - start_merge > 0:
                        worksheet.merge_range('B'+str(start_merge)+':B'+str(start_merge+count_vend), temp_vendor, normal_bold_border)
                    else:
                        worksheet.write(row+4 , 1, temp_vendor, normal_bold_border)
                    worksheet.write(row+5 , 7, sum_rp, format_number_bold)
                    worksheet.write(row+5 , 8, sum_total, format_number_bold)
                    worksheet.write(row+5 , 9, sum_ppn, format_number_bold)
                    temp_vendor = pos[0]
                    total_ppn += sum_ppn
                    total_discount += sum_rp
                    total_sales += sum_total
                    sum_rp = sum_total = sum_ppn = 0
                    count_vend = -1
                    row += 1
                    start_merge = row + 6
                    
                worksheet.write(row+5, 2, pos[2], normal_center_border) #period
                worksheet.write(row+5, 3, pos[3], normal_center_border) #product
                worksheet.write(row+5, 4, pos[4], format_number) #price
                worksheet.write(row+5, 5, pos[5], normal_center_border) #qty
                worksheet.write(row+5, 6, pos[6], normal_center_border) #persen
                worksheet.write(row+5, 7, discount, format_number)  # rp
                worksheet.write(row+5, 8, amount_total, format_number) #total
                worksheet.write(row+5, 9, taxed, format_number) #ppn 
                
                if pos[7] == 'product':
                        prod += pos[5]
                elif pos[7] == 'service':
                    serv += pos[5]
                    
                sum_rp += discount
                sum_total += amount_total
                sum_ppn += taxed
                row += 1
                
                count_of_sum += 1
                count_vend += 1
                temp_vendor = pos[0]
                
                if count_of_sum  == len(obj_pos): #last line of obj_pos
                    if (start_merge + count_vend) - start_merge > 0:
                        worksheet.merge_range('B'+str(start_merge)+':B'+str(start_merge+count_vend), temp_vendor, normal_bold_border)
                    else:
                        worksheet.write(row+4 , 1, temp_vendor, normal_bold_border)
                    worksheet.write(row+5 , 7, sum_rp, format_number_bold)
                    worksheet.write(row+5 , 8, sum_total, format_number_bold)
                    worksheet.write(row+5 , 9, sum_ppn, format_number_bold)
                    temp_vendor = pos[0]
                    total_ppn += sum_ppn
                    total_discount += sum_rp
                    total_sales += sum_total
            
            worksheet.write(row+7 , 1, 'Taxes (Rp)', normal_left_bold)     
            worksheet.write(row+8 , 1, 'PPN 10%', normal_left)
            worksheet.write(row+8 , 8, total_ppn, format_number_unborder)
            worksheet.write(row+9 , 1, 'Total Sales (Rp)', normal_left_bold)                        
            worksheet.write(row+9 , 8, total_sales, format_number_bold_unborder)  
            worksheet.write(row+10, 1,'Qty of Product (pcs)', normal_left)
            worksheet.write(row+10, 8, prod, format_number_unborder)
            worksheet.write(row+11, 1,'Qty of Treatment', normal_left)
            worksheet.write(row+11, 8, serv, format_number_unborder)               
            worksheet.write(row+12 , 1, 'Total Discount (Rp)', normal_left_bold)                        
            worksheet.write(row+12 , 8, total_discount, format_number_bold_unborder) 
            workbook.close()

            out = base64.encodestring(bz.getvalue())
            this.write({'state_x':'get', 'data_x':out, 'name': filename})

            ir_model_data = self.env['ir.model.data']
            bz.close()
            form_res = ir_model_data.get_object_reference('laporan_penjualan_promo_discount', 'laporan_promo_discount_report_wizard_view')
            form_id = form_res and form_res[1] or False
            
            return {
                'name': ('Download XLS'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'laporan.promo.discount.report.wizard',
                'res_id': this.id,
                'view_id': False,
                'views': [(form_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current'
            }

