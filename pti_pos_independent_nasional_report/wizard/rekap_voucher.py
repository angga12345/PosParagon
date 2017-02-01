from openerp import models, fields, api
from cStringIO import StringIO
from datetime import datetime, timedelta
import xlsxwriter
import base64
import time
import pytz


class RekapVoucherReportWizard(models.TransientModel):
    _name = "rekap.voucher.wizard"

    start_period = fields.Date(string="Start Period")
    end_period = fields.Date(string="End Period")
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    name = fields.Char('Filename', readonly=True)
    check_all=fields.Boolean('Check')
    data_x = fields.Binary('File', readonly=True)

    @api.multi
    def generate_excel_rekap_voucher(self):
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

            filename = 'Rekap Voucher.xls'

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
            normal_right_bold_border = workbook.add_format({'bold' :1,'valign':'bottom','align':'right'})
            normal_right_bold_border.set_text_wrap()
            normal_right_bold_border.set_font_name('Arial')
            normal_right_bold_border.set_font_size('10')
            normal_right_bold_border.set_border()
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
            format_number_center = workbook.add_format({'valign':'vcenter','align':'center'})
            format_number_center.set_num_format('#,##0.00')
            format_number_center.set_font_name('Arial')
            format_number_center.set_font_size('10')
            format_number_center.set_border()
            #################################################################################
            format_number_bold_unborder = workbook.add_format({'bold': 1,'valign':'vcenter','align':'right'})
            format_number_bold_unborder.set_num_format('#,##0.00')
            format_number_bold_unborder.set_font_name('Arial')
            format_number_bold_unborder.set_font_size('10')
            
            worksheet = workbook.add_worksheet("Rekap Voucher")
            worksheet.set_column('A:A', 10)
            worksheet.set_column('B:B', 40)
            worksheet.set_column('C:C', 15)
            worksheet.set_column('D:D', 7)
            worksheet.set_column('E:E', 10)
            
            worksheet.merge_range('A1:E1', 'REKAP VOUCHER', center_title)
            
            worksheet.write('B4','Start Period :',normal_left_bold)
            worksheet.write('B5', sp.strftime('%d %b %Y'),normal_left_bold)
            worksheet.write('C4', 'End Period :',normal_left_bold)
            worksheet.write('C5', ep.strftime('%d %b %Y'),normal_left_bold) 
            worksheet.write('E4', 'Print Date :',normal_left_bold)
            worksheet.write('E5', utc_tz.strftime('%d %b %Y %H:%M'), normal_left_bold) 
            
            worksheet.write('A6', 'Date', normal_bold_border)
            worksheet.write('B6', 'Nama Voucher',normal_bold_border)
            worksheet.write('C6', 'Nominal Voucher',normal_bold_border)
            worksheet.write('D6', 'Pcs', normal_bold_border)
            worksheet.write('E6', 'Jumlah', normal_bold_border)

            worksheet.freeze_panes(9,2)
            self.env.cr.execute("""
                select to_char(porder.date_order,'DD Mon YYYY'),ptemplate.name, abs(ptemplate.list_price) as price, 
                sum(pline.qty) as pcs,sum(round(abs(ptemplate.list_price)*pline.qty)) as jumlah,ptemplate.voucher
                    FROM pos_order porder 
                    join pos_order_line pline on porder.id = pline.order_id 
                    join product_product as pproduct on pproduct.id=pline.product_id
                    join product_template as ptemplate on pproduct.product_tmpl_id = ptemplate.id
                    join pos_session as psession on porder.session_id = psession.id
                    join pos_config as pconfig on psession.config_id = pconfig.id
                    where porder.date_order >= %s and porder.date_order <= %s and ptemplate.voucher=true and pconfig.stand_alone_categ = 'independent'
                    group by
                             to_char(porder.date_order,'DD Mon YYYY'), ptemplate.name,
                             abs(ptemplate.list_price),ptemplate.voucher
                        order by to_char(porder.date_order,'DD Mon YYYY')
                """, (start_period+' 00:00:00', end_period+' 23:59:59'))
            form_obj = self.env.cr.fetchall()

            row=1
            number = 1
            inc = 0
            sum_total=0.0
            
            for pos in form_obj:
                worksheet.write(row+5, 0, pos[0], normal_center_border)
                worksheet.write(row+5, 1, pos[1], normal_left_border)
                worksheet.write(row+5, 2, pos[2], format_number)
                worksheet.write(row+5, 3, pos[3], format_number_center)
                worksheet.write(row+5, 4, pos[4], format_number)
                number += 1 
                sum_total += pos[4]
                row +=1
                inc += 1
            string_total='A'+str((row+5)+1)+':B'+str((row+5)+1)
            string_kosong='C'+str((row+5)+1)+':D'+str((row+5)+1)
            worksheet.merge_range(string_total, 'TOTAL', normal_right_bold_border)
            worksheet.merge_range(string_kosong, ' ', normal_right_bold_border)
            worksheet.write(row+5, 4, sum_total, format_number_bold)          
            workbook.close()

            out = base64.encodestring(bz.getvalue())
            this.write({'state_x':'get', 'data_x':out, 'name': filename})

            ir_model_data = self.env['ir.model.data']
            bz.close()
            form_res = ir_model_data.get_object_reference('pti_pos_independent_nasional_report', 'independent_nasional_store_report_rekap_voucher_wizard_view')
            form_id = form_res and form_res[1] or False
            
            return {
                'name': ('Download XLS'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'rekap.voucher.wizard',
                'res_id': this.id,
                'view_id': False,
                'views': [(form_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current'
            }

