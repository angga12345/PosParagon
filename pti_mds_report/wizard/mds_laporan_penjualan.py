from openerp import models, fields, api
from cStringIO import StringIO
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta
import xlsxwriter
import base64
import time
from pytz import timezone
import pytz

    
class MdsLaporanPenjualanPerTransaksi(models.TransientModel):
    _name = "mds.laporan.penjualan.per.transaksi"

    store = fields.Many2one('pos.config', string="Store", domain=[('category_shop', '=','shop_in_shop_mds')])
    start_period = fields.Date(string="Start Period")
    end_period = fields.Date(string="End Period")
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    check_all = fields.Boolean('Check')

    @api.multi
    def generate_excel_mds(self):
        for this in self:
            start_period = this.start_period
            end_period = this.end_period
            today = datetime.now()
            sp=datetime.strptime(start_period, DEFAULT_SERVER_DATE_FORMAT)
            ep=datetime.strptime(end_period, DEFAULT_SERVER_DATE_FORMAT)
            bz = StringIO()
            workbook = xlsxwriter.Workbook(bz)

            filename = 'Lap. Penj. Per Transaksi.xlsx'

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
            format_number_nobold = workbook.add_format({'valign':'vcenter','align':'right'})
            format_number_nobold.set_num_format('#,##0.00')
            format_number_nobold.set_font_name('Arial')
            format_number_nobold.set_font_size('10')
            #################################################################################
            format_number = workbook.add_format({'valign':'vcenter','align':'right'})
            format_number.set_num_format('#,##0.00')
            format_number.set_font_name('Arial')
            format_number.set_font_size('10')
            format_number.set_border()

            
            worksheet = workbook.add_worksheet("report")
            worksheet.set_column('A:A', 20)
            worksheet.set_column('B:B', 20)
            worksheet.set_column('C:C', 20)
            worksheet.set_column('D:D', 20)
            worksheet.set_column('E:E', 20)
            worksheet.set_column('F:F', 20)
            worksheet.set_column('G:G', 20)
            worksheet.set_column('H:H', 20)
            worksheet.set_column('I:I', 15)
            worksheet.set_column('J:J', 10)
            worksheet.set_column('K:K', 10)
            worksheet.set_column('L:L', 15)
            
            worksheet.merge_range('A1:C1', 'Laporan Penjualan Per Transaksi', merge_formats)
            worksheet.write('A3','Start Period :',normal_left_bold)
            worksheet.write('A4', sp.strftime('%d %b %Y'),normal_left)
            worksheet.write('B3', 'End Period :',normal_left_bold)
            worksheet.write('B4', ep.strftime('%d %b %Y'),normal_left) 
            worksheet.write('C3', 'Print Date :',normal_left_bold)
            worksheet.write('C4', today.strftime('%d %b %Y %H:%M'),normal_left) 
            
            worksheet.write('A6', 'Date', normal_bold_border)
            worksheet.write('B6', 'Time',normal_bold_border)
            worksheet.write('C6', 'Nominal Transaksi', normal_bold_border)

            # how to get data
            row = 1
            number = 1
            count = 1
            total = 0

            self.env.cr.execute("""
                set datestyle=dmy;
                select po.date_order as ordat, po.amount_total_rel as amount
                from pos_order as po
                join pos_session as ps on ps.id = po.session_id
                join pos_config as pc on pc.id = ps.config_id
                where po.date_order::date >= %s and po.date_order::date <= %s and pc.name = %s
                group by po.date_order, po.amount_total_rel, po.id
                order by po.date_order
                """, (start_period, end_period, self.store.name))
#             form = self.env.cr.fetchall()
            result = self.env.cr.dictfetchall()
            for record in result:

                dates = record['ordat']
                times = record['ordat']
                dates1=dates.rpartition(':')[0]
                dates_fix = datetime.strptime(dates1, "%Y-%m-%d %H:%M")
                worksheet.write(row+5, 0, dates_fix.strftime('%d %b %Y'), normal_center_border)
                worksheet.write(row+5, 1, dates_fix.strftime('%H:%M'), normal_left_border)

                dates = datetime.strptime(dates1, "%Y-%m-%d %H:%M")
                times = datetime.strptime(dates1, "%Y-%m-%d %H:%M")
                
               
                _timezone='Asia/Jakarta'
                tz = timezone(_timezone)
                local_times=pytz.utc.localize(times, is_dst=None).astimezone(tz)     
                
#                 print (times.strftime('%H:%M'),"********************************************")     
#                 print (local_times.strftime('%H:%M'),"#########################################################")      
                
                worksheet.write(row+5, 0, dates.strftime('%d %b %Y'), normal_center_border)
                worksheet.write(row+5, 1, local_times.strftime('%H:%M'), normal_left_border)
                worksheet.write(row+5, 2, record['amount'], format_number)
                row = row + 1
                number = number + 1
                count = count + 1
                total += record['amount']
                value = len(result)
                
            avg = total / value
            worksheet.merge_range('A'+str(row+7)+':B'+str(row+7), 'Jumlah Transaksi', normal_left)
            worksheet.write(row+6 , 2, value, format_number_nobold)
            worksheet.merge_range('A'+str(row+8)+':B'+str(row+8), 'Average Transaksi Harian', normal_left)
            worksheet.write(row+7 , 2, avg, format_number_nobold)
            workbook.close()

            out = base64.encodestring(bz.getvalue())
            this.write({'state_x':'get', 'data_x':out, 'name': filename})
 
            ir_model_data = self.env['ir.model.data']
            bz.close()
            form_res = ir_model_data.get_object_reference("pti_mds_report", "mds_laporan_penjualan_per_transaksi_view")
            form_id = form_res and form_res[1] or False
            return {
                'name': ('Download XLS'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mds.laporan.penjualan.per.transaksi',
                'res_id': this.id,
                'view_id': False,
                'views': [(form_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current'
            }
