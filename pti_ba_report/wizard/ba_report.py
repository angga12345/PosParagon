from openerp import models, fields, api
from cStringIO import StringIO
from datetime import datetime, timedelta
import xlsxwriter
import base64
import time

    
class CurrentBussinessReportWizard(models.TransientModel):
    _name = "current.bussiness.report.wizard"

    store = fields.Many2one('pos.config', string="Store")
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

            filename = 'Penjualan Total Harian '+self.store.name+'.xlsx'

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

            
            worksheet = workbook.add_worksheet("report")
            worksheet.set_column('A:A', 5)
            worksheet.set_column('B:B', 17)
            worksheet.set_column('C:C', 15)
            worksheet.set_column('D:D', 18)
            worksheet.set_column('E:E', 15)
            worksheet.set_column('F:F', 18)
            worksheet.set_column('G:G', 20)
            worksheet.set_column('H:H', 15)
            worksheet.set_column('I:I', 15)
            worksheet.set_column('J:J', 10)
            worksheet.set_column('K:K', 10)
            worksheet.set_column('L:L', 15)
            
            worksheet.merge_range('A1:C1', 'Penjualan Total Harian', merge_formats)
            worksheet.write('B3','Start Period :',normal_left_bold)
            worksheet.write('B4', sp.strftime('%d %b %Y'),normal_left)
            worksheet.write('C3', 'End Period :',normal_left_bold)
            worksheet.write('C4', ep.strftime('%d %b %Y'),normal_left) 
            worksheet.write('D3', 'Print Date :',normal_left_bold)
            worksheet.write('D4', today.strftime('%d %b %Y %H:%M'),normal_left) 
            
            worksheet.write('A6', 'No.', normal_bold_border)
            worksheet.write('B6', 'Nama BA',normal_bold_border)
            worksheet.write('C6', 'Total Penjualan', normal_bold_border)

# how to get data
            row = 0
            number = 1
            count = 1
            total = 0

            self.env.cr.execute("""
                select distinct temp.user as BA, sum(temp.amount) as total
                from
                (select rp.name as user, po.amount_total_rel as amount
                from pos_order as po
                join pos_session as ps on ps.id = po.session_id
                join pos_config as pc on pc.id = ps.config_id
                join res_users as ru on ru.id=po.user_id
                join res_partner as rp on rp.id=ru.partner_id
                where po.date_order >= %s and po.date_order <= %s and pc.name = %s
                group by rp.name, po.amount_total_rel, po.id) as temp
                group by temp.user

                """, (start_period+' 00:00:00', end_period+' 23:59:59', self.store.name))
            form = self.env.cr.fetchall()
            for pos in form:
                worksheet.write(row+6, 0, number, normal_center_border)
                worksheet.write(row+6, 1, pos[0], normal_left_border)
                worksheet.write(row+6, 2, pos[1], format_number)
                row = row + 1
                number = number + 1
                count = count + 1
                total += pos[1]

            worksheet.merge_range('A'+str(row+7)+':B'+str(row+7),'TOTAL',merge_formats)
            worksheet.write(row+6 , 2, total, format_number_bold)
            workbook.close()

            out = base64.encodestring(bz.getvalue())
            this.write({'state_x':'get', 'data_x':out, 'name': filename})

            ir_model_data = self.env['ir.model.data']
            bz.close()
            form_res = ir_model_data.get_object_reference('pti_ba_report', 'current_bussiness_report_wizard_view')
            form_id = form_res and form_res[1] or False
            
            return {
                'name': ('Download XLS'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'current.bussiness.report.wizard',
                'res_id': this.id,
                'view_id': False,
                'views': [(form_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current'
            }

