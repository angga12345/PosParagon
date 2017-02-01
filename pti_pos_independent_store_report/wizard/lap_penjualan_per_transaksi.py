from openerp import models, fields, api
from cStringIO import StringIO
from datetime import datetime
import xlsxwriter
import base64
import time
import pytz


class LaporanPenjualanPerTransaksiReportWizard(models.TransientModel):
    _name = "laporan.penjualan.per.transaksi.report.wizard"

    start_period = fields.Date(string="Start Period")
    end_period = fields.Date(string="End Period")
    store = fields.Many2one("pos.config", string="Store",
                            domain=[('category_shop', '=', 'stand_alone'),
                                    ('stand_alone_categ', '=', 'independent')])
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)

    @api.multi
    def generate_excel(self):
        for this in self:
            start_period = this.start_period
            end_period = this.end_period
            sn = this.store.id
            today = datetime.now()
            timezone = pytz.timezone(self._context.get('tz') or 'UTC')
            utc_tz = pytz.utc.localize(today, '%d %b %Y %H:%M').astimezone(timezone)
            sp=datetime.strptime(start_period, '%Y-%m-%d')
            ep=datetime.strptime(end_period, '%Y-%m-%d')

            bz = StringIO()
            workbook = xlsxwriter.Workbook(bz)

            filename = 'Laporan Penjualan Per Transaksi '+this.store.name+'.xlsx'

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
            merge_formats.set_font_size('12')
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
            format_category = workbook.add_format({'bold': 1,'valign':'vcenter','align':'right'})
            format_category.set_num_format('#,##0.00')
            format_category.set_font_name('Arial')
            format_category.set_font_size('10')
            format_category.set_border()
            format_category.set_bg_color('#BDC3C7')
            #################################################################################
            format_total = workbook.add_format({'bold': 1,'valign':'vcenter','align':'right'})
            format_total.set_num_format('#,##0.00')
            format_total.set_font_name('Arial')
            format_total.set_font_size('10')
            format_total.set_border()
            format_total.set_bg_color('#99FFFF')
            #################################################################################
            bold_left_category = workbook.add_format({'bold': 1,'valign':'vcenter','align':'left'})
            bold_left_category.set_text_wrap()
            bold_left_category.set_border()
            bold_left_category.set_font_name('Arial')
            bold_left_category.set_font_size('10')
            bold_left_category.set_bg_color('#BDC3C7')
            #################################################################################
            merge_formats_category = workbook.add_format({'bold': 1,'align': 'center','valign': 'vcenter',})
            merge_formats_category.set_font_name('Arial')
            merge_formats_category.set_font_size('10')
            merge_formats_category.set_border()
            merge_formats_category.set_bg_color('#99FFFF')
            #################################################################################
            date_format = workbook.add_format({'num_format': 'd mmm yyyy', 'align':'center'})
            date_format.set_border()
            
            worksheet = workbook.add_worksheet("report")
            worksheet.set_column('A:A', 30)
            worksheet.set_column('B:B', 25)
            worksheet.set_column('C:C', 25)
                     
            worksheet.merge_range('A1:C1', 'Laporan Penjualan Per Transaksi', merge_formats)
            worksheet.write('A3','Store Name : '+this.store.name, normal_left_bold)
            worksheet.write('A4','Start Period : '+sp.strftime('%d %b %Y'), normal_left_bold)
            worksheet.write('B4','End Period : '+ep.strftime('%d %b %Y'), normal_left_bold)
            worksheet.write('C4','Print Date : '+utc_tz.strftime('%d %b %Y %H:%M'), normal_left_bold)

            worksheet.write('A6', 'Date', normal_bold_border )
            worksheet.write('B6', 'Time', normal_bold_border)
            worksheet.write('C6', 'Nominal Transaksi', normal_bold_border)
            
            row = 6
            jumlah_transaksi = 0
            
            user = self.env['res.users'].browse(self._uid)
            tz = pytz.timezone(user.tz) if user.tz else pytz.utc
            
            cr=self._cr
            cr.execute("""
                    select a.date_order, a.amount_total_rel from pos_order a
                    join pos_session b on b.id = a.session_id
                    join pos_config c on c.id = b.config_id
                    where c.id = %s AND a.date_order <= %s
                    AND c.stand_alone_categ = 'independent' 
                    AND a.date_order >= %s
                    """, (sn,end_period+' 23:59:59', start_period+' 00:00:00'))            
            orders = cr.fetchall()
            sum = 0
            for order in orders:         
                date = order[0]
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                date = pytz.utc.localize(date).astimezone(tz)
                date = datetime.strftime(date, '%Y-%m-%d %H:%M:%S') 
                time = date
                nominal = order[1]
                date = date[:10]
                date = datetime.strptime(date, "%Y-%m-%d")
                time = time[10:]
                time = time[:6]
    
                worksheet.write(row, 0, date, date_format)
                worksheet.write(row, 1, time, normal_center_border)
                worksheet.write(row, 2, nominal, format_number)
                sum += nominal
                row += 1 
                
            total = len(orders)
            average = sum/total
            
            worksheet.merge_range('A'+str(row+2)+':B'+str(row+2),'Jumlah Transaksi',normal_left_bold)
            worksheet.write(row+1, 2, total, format_number_bold_minbord)
            worksheet.merge_range('A'+str(row+3)+':B'+str(row+3),'Average Transaksi Harian',normal_left_bold)
            worksheet.write(row+2, 2, average, format_number_bold_minbord)

            workbook.close()

            out = base64.encodestring(bz.getvalue())
            this.write({'state_x':'get', 'data_x':out, 'name': filename})

            ir_model_data = self.env['ir.model.data']
            bz.close()
            form_res = ir_model_data.get_object_reference('pti_wbh_pos_report', 'sales_each_transaction_report_wizard_view')
            form_id = form_res and form_res[1] or False
            
            return {
                'name': ('Download XLS'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'laporan.penjualan.per.transaksi.report.wizard',
                'res_id': this.id,
                'view_id': False,
                'views': [(form_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current'
            }
                
        
