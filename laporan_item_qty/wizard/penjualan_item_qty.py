from openerp import models, fields, api
from cStringIO import StringIO
from datetime import datetime, timedelta
import xlsxwriter
import base64
import time
import pytz


class LaporanItemQtyReportWizard(models.TransientModel):
    _name = "laporan.item.qty.report.wizard"
    
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
            timezone = pytz.timezone(self._context.get('tz') or 'UTC')
            utc_tz = pytz.utc.localize(today, '%d %b %Y %H:%M').astimezone(timezone)
            sp=datetime.strptime(start_period, '%Y-%m-%d')
            ep=datetime.strptime(end_period, '%Y-%m-%d')
            
            bz = StringIO()
            workbook = xlsxwriter.Workbook(bz)
            filter = self.filter
            if filter == '1': 
                filename = 'Laporan Penjualan per Item per Qty per Store.xls'
            else:
                brand_id = self.brand_id.id
                brand = self.brand_id.name
                filename = 'Laporan Penjualan per Item per Qty per Store per-'+brand+'.xls'
            
            #### STYLE
            #################################################################################
            left_title = workbook.add_format({'bold': 1,'valign':'vcenter','align':'left'})
            left_title.set_text_wrap()
            left_title.set_font_name('Arial')
            left_title.set_font_size('12')
            #################################################################################
            normal_left = workbook.add_format({'valign':'bottom','align':'left'})
            normal_left.set_text_wrap()
            normal_left.set_font_name('Arial')
            normal_left.set_font_size('10')
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
            center_left = workbook.add_format({'valign':'vcenter','align':'left'})
            center_left.set_text_wrap()
            center_left.set_font_name('Arial')
            center_left.set_font_size('10')
            center_left.set_border()
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
            format_number_unborder.set_num_format('#,##0')
            format_number_unborder.set_font_name('Arial')
            format_number_unborder.set_font_size('10') 
            #################################################################################
            normal_left_unborder = workbook.add_format({'valign':'bottom','align':'left'})
            normal_left_unborder.set_text_wrap()
            normal_left_unborder.set_font_name('Arial')
            normal_left_unborder.set_font_size('10') 

            
            worksheet = workbook.add_worksheet("report")
            worksheet.set_column('A:A', 20)
            worksheet.set_column('B:B', 20)
            worksheet.set_column('C:C', 5)
            worksheet.set_column('D:D', 60)
            worksheet.set_column('E:E', 8)
            worksheet.set_column('F:F', 8)

            
            worksheet.merge_range('A1:B1', 'Laporan Penjualan Per Item / Per SKU / Per Store', left_title)
            worksheet.write('A4','Start Period :',normal_left_bold)
            worksheet.write('A5', sp.strftime('%d %b %Y'),normal_left)
            worksheet.write('B4', 'End Period :',normal_left_bold)
            worksheet.write('B5', ep.strftime('%d %b %Y'),normal_left) 
            worksheet.write('D4', 'Print Date :',normal_left_bold)
            worksheet.write('D5', utc_tz.strftime('%d %b %Y %H:%M'),normal_left) 
            
            
            worksheet.write('A6', 'DC', normal_bold_border)
            worksheet.write('B6', 'Store Name',normal_bold_border)
            worksheet.write('C6', 'No.', normal_bold_border)
            worksheet.write('D6', 'Product', normal_bold_border)
            worksheet.write('E6', 'SKU', normal_bold_border)
            worksheet.write('F6', 'Qty', normal_bold_border)

            worksheet.freeze_panes(6,6)
            
            if filter == '1':
                print '11111111111111111111111111',filter
                self.env.cr.execute("""
                    select 
                        dcpartner.name as dc, pconfig.name as shop, pproduct.name_template as product, porder.shop_identifier_origin as "SKU", round(sum(pline.qty)) as qty, porder.shop_identifier_period as "SKU Promo" 
                    from pos_order porder 
                    join pos_order_line pline on porder.id = pline.order_id
                    join product_product pproduct on pproduct.id = pline.product_id
                    join pos_session psession on porder.session_id = psession.id
                    join pos_config pconfig on psession.config_id = pconfig.id
                    join stock_location slocation on slocation.id = pconfig.stock_location_id
                    join res_partner rpartner on rpartner.id = slocation.partner_id
                    join res_partner dcpartner on rpartner.dc_id = dcpartner.id 
                    where porder.date_order >=%s AND porder.date_order <= %s and pconfig.category_shop='shop_in_shop_mds'
                    group by
                            dcpartner.name,pconfig.name,
                            pproduct.name_template, 
                            porder.shop_identifier_period,
                            porder.shop_identifier_origin,
                            pline.price_unit, pline.price_unit
                    order by pconfig.name, pproduct.name_template
     
                    """, (start_period+' 00:00:00', end_period+' 23:59:59'))
                
            else:
                print '22222222222222222222222222',filter
                self.env.cr.execute("""
                    select 
                        dcpartner.name as dc, pconfig.name as shop, pproduct.name_template as product, porder.shop_identifier_origin as "SKU", round(sum(pline.qty)) as qty, porder.shop_identifier_period as "SKU Promo" 
                    from pos_order porder 
                    join pos_order_line pline on porder.id = pline.order_id
                    join product_product pproduct on pproduct.id = pline.product_id
                    join pos_session psession on porder.session_id = psession.id
                    join pos_config pconfig on psession.config_id = pconfig.id
                    join stock_location slocation on slocation.id = pconfig.stock_location_id
                    join res_partner rpartner on rpartner.id = slocation.partner_id
                    join res_partner dcpartner on rpartner.dc_id = dcpartner.id 
                    where porder.date_order >=%s AND porder.date_order <= %s and pconfig.tags=%s and pconfig.category_shop='shop_in_shop_mds'
                    group by
                            dcpartner.name,pconfig.name,
                            pproduct.name_template, 
                            porder.shop_identifier_period,
                            porder.shop_identifier_origin,
                            pline.price_unit, pline.price_unit
                    order by pconfig.name, pproduct.name_template
     
                    """, (start_period+' 00:00:00', end_period+' 23:59:59',brand_id))
            form_obj = self.env.cr.fetchall()

            sku_list = {}
            row=1
            number = 1
            inc = 0
            dc=0
            string_dc=''
            store=0
            string_store=''
            for pos in form_obj:
                worksheet.write(row+5, 0, pos[0], normal_left_border)
                worksheet.write(row+5, 1, pos[1], normal_left_border)
                worksheet.write(row+5, 2, row, normal_center_border)
                worksheet.write(row+5, 3, pos[2], normal_left_border)
                if pos[3] and pos[5]:
                    sku = pos[5]
                elif pos[3] and not pos[5]:
                    sku = pos[3]
                elif not pos[3] and pos[5]:
                    sku = pos[5]
                elif not pos[3] and not pos[5]:
                    sku = ""
                #manipulation sku in 8digit   
                if len(sku) > 8:
                    sku = sku[4:][:-1]
                worksheet.write(row+5, 4, sku, normal_center_border)
                worksheet.write(row+5, 5, pos[4], normal_center_border)

                sku_list.update({inc : [sku,pos[4]]})            
                number += 1
                row += 1
                if len(form_obj)-1==inc or pos[0]!=form_obj[inc+1][0]:
                    if dc==0:
                        string_dc = 'A7:A'+str(row+5)
                    else :
                        string_dc = 'A'+str(((row+5)-number)+2)+':A'+str((row+6)-1)
#                     print string_dc
#                     print dc
                    dc += 1
                    worksheet.merge_range(string_dc, pos[0], center_left)
                
                if len(form_obj)-1==inc or pos[1]!=form_obj[inc+1][1]:
                    print number
                    if store==0:
                        string_store = 'B7:B'+str(row+5)
                    else :
                        string_store = 'B'+str(((row+5)-number)+2)+':B'+str((row+6)-1)
                    store += 1
                    number = 1
                    worksheet.merge_range(string_store, pos[1], center_left)
 
                inc += 1
            
               
            sku_set = []
            for sku in sku_list.values():
                sku_set.append(sku[0])
     
            sku_set = list(set(sku_set))
            sku_values = dict()
            for  sku_set in sku_set:
                qty_total=0            
                for sku in sku_list.values(): 
                    if sku_set == sku[0]:
                        qty_total += sku[1]                                      
                sku_values.update({sku_set : qty_total})
                 
            worksheet.write(row+6 , 1, 'Qty of product', normal_left_bold)
            for key, value in sku_values.iteritems():
                row += 1
                #manipulation sku in 8digit
                if len(key) > 8:
                    key = key[4:][:-1]
#                 worksheet.write_rich_string(row+6, 1, 'SKU ', str(key), ' (pcs)', normal_left_unborder)
                worksheet.write(row+6, 1, 'SKU '+ str(key)+ ' (pcs)', normal_left_unborder)
                worksheet.write(row+6, 4, value, format_number_unborder)     
                        
            workbook.close()

            out = base64.encodestring(bz.getvalue())
            this.write({'state_x':'get', 'data_x':out, 'name': filename})

            ir_model_data = self.env['ir.model.data']
            bz.close()
            form_res = ir_model_data.get_object_reference('laporan_item_qty', 'laporan_item_qty_report_wizard_view')
            form_id = form_res and form_res[1] or False
            
            return {
                'name': ('Download XLS'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'laporan.item.qty.report.wizard',
                'res_id': this.id,
                'view_id': False,
                'views': [(form_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current'
            }

