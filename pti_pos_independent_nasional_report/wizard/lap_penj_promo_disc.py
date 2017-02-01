from openerp import models, fields, api
from cStringIO import StringIO
from datetime import datetime, timedelta
import xlsxwriter
import base64
import time
from jinja2.runtime import to_string

    
class LaporanPenjPromoDiscReportWizard(models.TransientModel):
    _name = "lap.penj.promo.disc.wizard"

    start_period = fields.Date(string="Start Period")
    end_period = fields.Date(string="End Period")
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    check_all=fields.Boolean('Check')

    @api.multi
    def generate_excel_lap_penj_promo_disc(self):
        form_bc_obj = self.env['pos.order']
        for this in self:
            start_period = this.start_period
            end_period = this.end_period
            today = datetime.now()
            sp=datetime.strptime(start_period, '%Y-%m-%d')
            ep=datetime.strptime(end_period, '%Y-%m-%d')
            
            bz = StringIO()
            workbook = xlsxwriter.Workbook(bz)

            filename = 'Lap Penj Promo Disc.xls'


            #### STYLE
            #################################################################################
            center_title = workbook.add_format({'bold': 1,'valign':'vcenter','align':'center'})
            center_title.set_text_wrap()
            center_title.set_font_name('Arial')
            center_title.set_font_size('12')
            #################################################################################
            normal_left = workbook.add_format({'valign':'bottom','align':'left'})
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

            
            worksheet = workbook.add_worksheet("Lap Penj Promo Disc per Store")
            worksheet.set_column('A:A', 25)
            worksheet.set_column('B:B', 55)
            worksheet.set_column('C:C', 10)
            worksheet.set_column('D:D', 6)
            worksheet.set_column('E:E', 4)
            worksheet.set_column('F:F', 14)
            worksheet.set_column('G:G', 16)
            worksheet.set_column('H:H', 14)
            
            worksheet.merge_range('A1:H1', 'Laporan Penjualan Promo Discount', center_title)
            worksheet.write('A5','Start Period :',normal_left_bold)
            worksheet.write('A6', sp.strftime('%d %b %Y'),normal_left)
            worksheet.write('B5', 'End Period :',normal_left_bold)
            worksheet.write('B6', ep.strftime('%d %b %Y'),normal_left) 
            worksheet.write('D5', 'Print Date :',normal_left_bold)
            worksheet.write('D6', today.strftime('%d %b %Y %H:%M'),normal_left) 
            
            worksheet.merge_range('A8:A9', 'Period Promo', normal_bold_border)
            worksheet.merge_range('B8:B9', 'Product', normal_bold_border)
            worksheet.merge_range('C8:C9', 'Price', normal_bold_border)
            worksheet.merge_range('D8:D9', 'Qty', normal_bold_border)
            worksheet.merge_range('E8:F8', 'Disc.', normal_bold_border)
            worksheet.write('E9', '%', normal_bold_border)
            worksheet.write('F9', 'Rp', normal_bold_border)
            worksheet.merge_range('G8:G9', 'Total', normal_bold_border)
            worksheet.merge_range('H8:H9', 'Ppn', normal_bold_border)
            worksheet.freeze_panes(9,2)
            
            self.env.cr.execute("""
                select  to_char(ppricelistitem.date_start,'DD Mon YYYY')|| ' - ' ||to_char(ppricelistitem.date_end, 'DD Mon YYYY') as period_promo,
                pproduct.name_template as Product, pline.price_unit as Price, ptemplate.type as tipe,
                sum(pline.qty) as Qty, ppricelistitem.price_discount,
                round((pline.price_unit*sum(pline.qty))*(ppricelistitem.price_discount/100),2) as Rp,
                round((pline.price_unit*sum(pline.qty)-((pline.price_unit*sum(pline.qty))*(ppricelistitem.price_discount/100))),2) as Total,
                round((pline.price_unit*sum(pline.qty)-((pline.price_unit*sum(pline.qty))*(ppricelistitem.price_discount/100)))*0.1,2) as Ppn
                from pos_order as porder 
                join pos_order_line as pline on porder.id = pline.order_id 
                join product_pricelist as ppricelist on porder.pricelist_id = ppricelist.id
                join product_pricelist_item as ppricelistitem on ppricelist.id = ppricelistitem.pricelist_id
                join product_product as pproduct on pproduct.id = pline.product_id
                join product_template as ptemplate on pproduct.product_tmpl_id = ptemplate.id
                join pos_session as psession on porder.session_id = psession.id
                join pos_config as pconfig on psession.config_id = pconfig.id
                join stock_location slocation on slocation.id = pconfig.stock_location_id
                join res_partner rpartner on rpartner.id = slocation.partner_id
                join res_partner dcpartner on rpartner.dc_id = dcpartner.id 
                where ppricelistitem.date_start >= %s AND ppricelistitem.date_end <= %s AND pconfig.stand_alone_categ = 'independent'
                group by
                pconfig.name,
                            pconfig.name, pproduct.name_template, ppricelistitem.date_start, 
                            ppricelistitem.date_end, pproduct.name_template, ptemplate.type,
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
            tipe_list = {}
            

            for pos in obj_pos:
                worksheet.write(row+8, 0, pos[0], normal_left_border)
                worksheet.write(row+8, 1, pos[1], normal_left_border)
                worksheet.write(row+8, 2, pos[2], format_number)
                tipe = pos[3]
                worksheet.write(row+8, 3, pos[4], format_number)
                worksheet.write(row+8, 4, pos[5], normal_center_border)
                worksheet.write(row+8, 5, pos[6], normal_center_border)
                worksheet.write(row+8, 6, pos[7], format_number)
                worksheet.write(row+8, 7, pos[8], format_number)
                
                tipe_list.update({ inc : [tipe,pos[4]]})
#                 sum_qt += pos[4]  
                sum_disc += pos[6]
                sum_total += pos[7]
                sum_ppn += pos[8]
                number += 1
                row +=1
                
                    
                if len(obj_pos)-1==inc:
                    worksheet.write(row+8 , 0, '', normal_left_border)
                    worksheet.write(row+8 , 1, '', normal_left_border)
                    worksheet.write(row+8 , 2, '', normal_left_border)
                    worksheet.write(row+8 , 3, '', normal_left_border)
                    worksheet.write(row+8 , 4, '', normal_left_border)       
                    worksheet.write(row+8 , 5, sum_disc, format_number_bold)        
                    worksheet.write(row+8 , 6, sum_total, format_number_bold)  
                    worksheet.write(row+8 , 7, sum_ppn, format_number_bold)
                    
                    number = 1
                    row = row+1 
                inc += 1
                     
            tipe_set = []
            for tipe in tipe_list.values():
                tipe_set.append(tipe[0])
    
            tipe_set = list(set(tipe_set))
            tipe_values = dict()
            for tipe_set in tipe_set:
                tipe_total=0            
                for tipe in tipe_list.values():               
                    if tipe_set == tipe[0]:
                        tipe_total += tipe[1]                
                tipe_values.update({tipe_set : tipe_total})    
    
            
            worksheet.write(row+9 , 0, 'Taxes (Rp)', normal_left_bold)     
            worksheet.write(row+10 , 0, 'PPN 10%', normal_left)
            worksheet.write(row+10 , 6, sum_ppn, format_number_unborder)  
            worksheet.write(row+11 , 0, 'Total Sales (Rp)', normal_left_bold)
            worksheet.write(row+11 , 6, sum_total, format_number_bold_unborder)                            
            for key, value in tipe_values.iteritems():
                row += 1
                if key == 'product':
                    worksheet.write(row+11, 0, 'Qty of Product (Pcs)', normal_left_bold)
                    if value != 0:
                        worksheet.write(row+11, 6, value, format_number_unborder)
                    else:
                        worksheet.write(row+11, 6, 0, format_number_unborder)
                elif key == 'service':
                    worksheet.write(row+11, 0, 'Qty of Treatment', normal_left_bold)
                    if value != 0:
                        worksheet.write(row+11, 6, value, format_number_unborder)
                    else:
                        worksheet.write(row+11, 6, 0, format_number_unborder)
                else:
                    stringnya = 'Qty of '+key.title()
                    worksheet.write(row+11, 0, stringnya, normal_left_bold)
                    if value != 0:
                        worksheet.write(row+11, 6, value, format_number_unborder)
                    else:
                        worksheet.write(row+11, 6, 0, format_number_unborder)

                          
            worksheet.write(row+12 , 0, 'Total Discount (Rp)', normal_left_bold)                        
            worksheet.write(row+12 , 6, sum_disc, format_number_bold_unborder) 
            workbook.close()

            out = base64.encodestring(bz.getvalue())
            this.write({'state_x':'get', 'data_x':out, 'name': filename})

            ir_model_data = self.env['ir.model.data']
            bz.close()
            form_res = ir_model_data.get_object_reference('pti_pos_independent_nasional_report', 'independent_nasional_store_report_lap_penj_promo_disc_wizard_view')
            form_id = form_res and form_res[1] or False                                             
            
            return {
                'name': ('Download XLS'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'lap.penj.promo.disc.wizard',
                'res_id': this.id,
                'view_id': False,
                'views': [(form_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current'
            }

