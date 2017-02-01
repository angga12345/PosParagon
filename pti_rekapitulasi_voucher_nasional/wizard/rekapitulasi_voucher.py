from openerp import models, fields, api
from cStringIO import StringIO
from datetime import datetime, timedelta
import xlsxwriter
import base64
import time
import pytz


class RekapitulasiVoucher(models.TransientModel):
    _name = "rekap.voucher.nasional"

    start_period = fields.Date(string="Start Period")
    end_period   = fields.Date(string="End Period")
    state_x      = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x       = fields.Binary('File', readonly=True)
    name         = fields.Char('Filename', readonly=True)

    @api.multi
    def generate_excel_rekap_voucher(self):
        form_bc_obj = self.env['pos.order.line']

        start_period = self.start_period
        end_period = self.end_period
        today = datetime.now()
        timezone = pytz.timezone(self._context.get('tz') or 'UTC')
        utc_tz = pytz.utc.localize(today, '%d %b %Y %H:%M').astimezone(timezone)
        sp=datetime.strptime(start_period, '%Y-%m-%d')
        ep=datetime.strptime(end_period, '%Y-%m-%d')
        
        bz = StringIO()
        workbook = xlsxwriter.Workbook(bz)

        filename = 'WBH Nasional Rekapitulasi Penggunaan Voucher.xlsx'

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
        normal_center_unborder_bold = workbook.add_format({'bold':1, 'valign':'bottom','align':'center'})
        normal_center_unborder_bold.set_text_wrap()
        normal_center_unborder_bold.set_font_name('Arial')
        normal_center_unborder_bold.set_font_size('10')        
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
        normal_center_border = workbook.add_format({'align':'center'})
        normal_center_border.set_text_wrap()
        normal_center_border.set_font_name('Arial')
        normal_center_border.set_font_size('10')
        normal_center_border.set_border()
        #################################################################################
        normal_vcenter_border = workbook.add_format({'valign':'vcenter', 'align':'center'})
        normal_vcenter_border.set_text_wrap()
        normal_vcenter_border.set_font_name('Arial')
        normal_vcenter_border.set_font_size('10')
        normal_vcenter_border.set_border()        
        #################################################################################
        normal_center_border_bold = workbook.add_format({'bold' : 1, 'valign':'bottom','align':'center'})
        normal_center_border_bold.set_text_wrap()
        normal_center_border_bold.set_font_name('Arial')
        normal_center_border_bold.set_font_size('10')
        normal_center_border_bold.set_border()        
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
        
    
        worksheet = workbook.add_worksheet("report")
        worksheet.freeze_panes(9,2)
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 50)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 5)
        worksheet.set_column('G:G', 10)
        
        worksheet.merge_range('C1:E1', 'REKAPITULASI PENGGUNAAN VOUCHER', center_title)
        worksheet.write('A4','Start Period :', normal_left_bold)
        worksheet.write('A5', sp.strftime('%d %b %Y'), normal_left_bold)
        worksheet.write('C4', 'End Period :', normal_left_bold)
        worksheet.write('C5', ep.strftime('%d %b %Y'), normal_left_bold)
        worksheet.write('E4', 'Print Date :', normal_left_bold)
        worksheet.write('E5', utc_tz.strftime('%d %b %Y %H:%M'), normal_left_bold)

        worksheet.write('A6', 'DC', normal_center_border_bold)
        worksheet.write('B6', 'Store name', normal_center_border_bold)
        worksheet.write('C6', 'Date', normal_center_border_bold)
        worksheet.write('D6', 'Nama Voucher', normal_center_border_bold)
        worksheet.write('E6', 'Nominal Voucher', normal_center_border_bold)
        worksheet.write('F6', 'Pcs', normal_center_border_bold)
        worksheet.write('G6', 'Jumlah', normal_center_border_bold)

        self.env.cr.execute("""
            SELECT dcpartner.name dc, pconfig.name as shop, to_char(porder.date_order,'DD Mon YYYY') date_order, pproduct.name_template nama_voucher, 
              abs(ptemplate.list_price) nominal_price, sum(pline.qty) pcs, abs(ptemplate.list_price*sum(pline.qty)) jumlah
              FROM pos_order porder 
              LEFT JOIN pos_order_line pline on porder.id = pline.order_id 
              JOIN pos_session psession on porder.session_id = psession.id
              JOIN pos_config pconfig on psession.config_id = pconfig.id
              JOIN product_product pproduct on pproduct.id = pline.product_id
              JOIN product_template ptemplate on ptemplate.id = pproduct.product_tmpl_id
              JOIN stock_location slocation on slocation.id = pconfig.stock_location_id
              JOIN res_partner rpartner on rpartner.id = slocation.partner_id
              JOIN res_partner dcpartner on rpartner.dc_id = dcpartner.id 
            WHERE porder.date_order >= %s AND porder.date_order <= %s AND pconfig.category_shop = 'stand_alone' and pproduct.voucher=true
            GROUP BY dcpartner.name, pconfig.name, to_char(porder.date_order,'DD Mon YYYY'), pproduct.name_template, ptemplate.list_price, ptemplate.voucher
            ORDER BY pconfig.name, to_char(porder.date_order,'DD Mon YYYY') ASC
            """, (start_period+' 00:00:00', end_period+' 23:59:59'))
        
        obj_pos = self.env.cr.dictfetchall()                         

        inc = 0
        row = 6
        number = 1
        sum_total = 0 
        shop_merge = 6
        date_merge = 0

        for pos in obj_pos:
            date_order = pos['date_order']
            print date_order
     
            if len(obj_pos)-1 != inc and date_order == obj_pos[inc+1]['date_order']:
                date_merge += 1
            else:
                print date_merge
                if date_merge > 0 :
                    worksheet.merge_range('C'+str((row-date_merge)+1)+':'+'C'+str(row+1), date_order, normal_vcenter_border)
                else :
                    worksheet.write(row, 2, date_order, normal_center_border)                
                date_merge = 0
            print date_order, "++++++++"

            worksheet.write(row, 0, pos['dc'], normal_center_border)
            worksheet.write(row, 3, pos['nama_voucher'], normal_left_border)
            worksheet.write(row, 4, pos['nominal_price'], format_number)
            worksheet.write(row, 5, pos['pcs'], format_number)
            worksheet.write(row, 6, pos['jumlah'], format_number)
            sum_total += pos['jumlah']

            if len(obj_pos)-1==inc or pos['shop'] != obj_pos[inc+1]['shop']:
                if shop_merge != row:
                    worksheet.merge_range('B'+str(shop_merge+1)+':'+'B'+str(row+1), pos['shop'], normal_vcenter_border)
                else:
                    worksheet.write(row, 1, pos['shop'], normal_center_border)

                row += 1
                worksheet.write(row, 0, '', normal_center_border)
                worksheet.write(row, 1, '', normal_center_border)
                worksheet.merge_range('C'+str(row+1)+':'+'F'+str(row+1), 'TOTAL', normal_center_border_bold)
                worksheet.write(row, 6, sum_total, format_number_bold)
                shop_merge = row+1
                sum_total = 0
                number = 1

            number +=  1
            row+=1
            inc += 1
        workbook.close()

        out = base64.encodestring(bz.getvalue())
        self.write({'state_x':'get', 'data_x':out, 'name': filename})

        ir_model_data = self.env['ir.model.data']
        bz.close()
        form_res = ir_model_data.get_object_reference('pti_rekapitulasi_voucher_nasional', 'rekap_voucher_nasional_wizard_view')
        form_id = form_res and form_res[1] or False
        
        return {
            'name': ('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'rekap.voucher.nasional',
            'res_id': self.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }


