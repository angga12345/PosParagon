from openerp import models, fields, api
from cStringIO import StringIO
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta
import xlsxwriter
import base64
import time

type_shop = [
             ('stand_alone', 'Stand Alone')
            ]
    
class ReportRekapEDCWBHPerStore(models.TransientModel):
    _name = "report.rekap.edc.wbh.per.store"
 
    start_period = fields.Date(string="Start Period")
    end_period = fields.Date(string="End Period")
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    store = fields.Many2one('pos.config', string="Store",selection=type_shop)
    
    def daterange(self, d1, d2):
        return (d1 + timedelta(days=i) for i in range((d2 - d1).days + 1))

    @api.multi
    def generate_excel_wbh_per_store(self):
        form_bc_obj = self.env['pos.order']
        for this in self:
            start_period = this.start_period
            end_period = this.end_period
            today = datetime.now()
            sp=datetime.strptime(start_period, DEFAULT_SERVER_DATE_FORMAT)
            ep=datetime.strptime(end_period, DEFAULT_SERVER_DATE_FORMAT)
            
            bz = StringIO()
            workbook = xlsxwriter.Workbook(bz)
 
            filename = 'Rekap EDC WBH Per Store.xlsx'
 
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
            normal_left_bold.set_font_size('11')
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
            normal_bold_border.set_font_size('11')
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
            
            # Add a number format for cells with money.
            money_format = workbook.add_format({'valign':'bottom','align':'right'})
            money_format.set_num_format('#,##0.00')
            money_format.set_text_wrap()
            money_format.set_font_name('Arial')
            money_format.set_font_size('10')
            money_format.set_border()
 
             
            worksheet = workbook.add_worksheet("report")
            worksheet.set_column('A:A', 11)
            worksheet.set_column('B:B', 11)
            worksheet.set_column('C:C', 11)
            worksheet.set_column('D:D', 11)
            worksheet.set_column('E:E', 11)
            worksheet.set_column('F:F', 11)
            worksheet.set_column('G:G', 11)
            worksheet.set_column('H:H', 11)
            worksheet.set_column('I:I', 15)
            worksheet.set_column('J:J', 10)
            worksheet.set_column('K:K', 10)
            worksheet.set_column('L:L', 15)
            worksheet.set_row(5, 55)
             
            worksheet.merge_range('A1:F1', 'REKAPITULASI TRANSAKSI ELECTRONIC DATA CAPTURE (EDC)', merge_formats)
            
            worksheet.write('A3', 'Store Name :', normal_left_bold)
            worksheet.merge_range('B3:F3', self.store.name, normal_left)
            worksheet.write('A4', 'Start Period :', normal_left_bold)
            worksheet.write('A5', sp.strftime('%d %b %Y'),normal_left)
            worksheet.write('C4', 'End Period :', normal_left_bold)
            worksheet.write('C5', ep.strftime('%d %b %Y'),normal_left) 
            worksheet.write('E4', 'Print Date :', normal_left_bold)
            worksheet.merge_range('E5:F5', today.strftime('%d %b %Y'),normal_left)
            
            worksheet.write('A6', 'Date', normal_bold_border)
            worksheet.write('B6', 'Trace No.', normal_bold_border)
            worksheet.write('C6', 'Appr. Code', normal_bold_border)
            worksheet.write('D6', 'Bank', normal_bold_border)
            worksheet.write('E6', 'Jumlah', normal_bold_border)
            worksheet.write('F6', 'Total (Akumulasi Transaksi Harian)', normal_bold_border)
            
            worksheet.freeze_panes(8,2)
 
            # how to get data
            row = 1

            total_amount = 0
            amount = 0 
            for d in self.daterange(sp, ep):
                dl = []
                var_loop_date = d.date();#datetime.datetime to date
                self.env.cr.execute("""
                    set datestyle=dmy;
                    select pc.name, po.date_order as ordat, po.amount_total_rel as amount, aj.type, acbstl.trace_no as traceno, acbstl.appr_code as apprcode
                    from account_journal as aj
                    join account_bank_statement_line as acbstl on acbstl.journal_id = aj.id
                    join account_bank_statement as acbst on acbst.id = acbstl.statement_id
                    join pos_order as po on po.id = acbstl.pos_statement_id
                    join pos_session as ps on ps.id = po.session_id
                    join pos_config as pc on pc.id = ps.config_id
                    where po.date_order::date BETWEEN %s and %s and aj.type = 'bank' and pc.name = %s
                    group by po.date_order, po.amount_total_rel, aj.type, acbstl.trace_no, acbstl.appr_code, pc.name
                    order by po.date_order
                    """, (sp, ep, self.store.name))
     
                result = self.env.cr.dictfetchall()
                flag = False;
                
                for qry in result:
                    var_loop_qry_date = datetime.strptime(qry['ordat'] , '%Y-%m-%d %H:%M:%S').date();#str to datetime.date
                    if var_loop_qry_date == var_loop_date:
                        total_amount = total_amount + qry['amount']
                        worksheet.write(row+5, 0, var_loop_qry_date.strftime('%d %b %Y'), normal_center_border)
                        worksheet.write(row+5, 1, qry['traceno'], normal_left_border)
                        worksheet.write(row+5, 2, qry['apprcode'], normal_left_border)
                        worksheet.write(row+5, 3, '', normal_left_border)
                        worksheet.write_number(row+5, 4, qry['amount'], money_format)
                        worksheet.write_number(row+5, 5, total_amount, money_format)
                        flag = True;
                        row = row + 1;
                
                if flag == False:
                    worksheet.write(row+5, 0, var_loop_date.strftime('%d %b %Y'), normal_center_border)
                    worksheet.write(row+5, 1, '', normal_left_border)
                    worksheet.write(row+5, 2, '', normal_left_border)
                    worksheet.write(row+5, 3, '', normal_left_border)
                    worksheet.write_number(row+5, 4, amount, money_format)
                    worksheet.write_number(row+5, 5, total_amount, money_format)
                    row = row + 1;
            
            
            total_menotal = 'A'+str(row+6)+':E'+str(row+6)
            total_semua = 'F'+str(row+6)
            worksheet.merge_range(total_menotal, 'TOTAL', merge_formats)
            worksheet.write(total_semua, total_amount, money_format)     

            workbook.close()
 
            out = base64.encodestring(bz.getvalue())
            this.write({'state_x':'get', 'data_x':out, 'name': filename})
  
            ir_model_data = self.env['ir.model.data'] 
            bz.close()
            form_res = ir_model_data.get_object_reference("pti_pos_rekap_edc", "report_edc_wbh_per_store")
            form_id = form_res and form_res[1] or False
            return {
                'name': ('Download XLS'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'report.rekap.edc.wbh.per.store',
                'res_id': this.id,
                'view_id': False,
                'views': [(form_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current'
            }
