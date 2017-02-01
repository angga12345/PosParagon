from openerp import models, fields, api
from cStringIO import StringIO
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta
import xlsxwriter
import base64
import time
import numpy as np


    
class ReportRekapEDCWBHNasional(models.TransientModel):
    _name = "report.rekap.edc.wbh.nasional"
 
    start_period = fields.Date(string="Start Period")
    end_period = fields.Date(string="End Period")
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    
    def daterange(self, d1, d2):
        return (d1 + timedelta(days=i) for i in range((d2 - d1).days + 1))
    
    @api.multi
    def generate_excel_wbh_nasional(self):
        form_bc_obj = self.env['pos.order']
        for this in self:
            start_period = this.start_period
            end_period = this.end_period
            today = datetime.now()
            sp=datetime.strptime(start_period, DEFAULT_SERVER_DATE_FORMAT)
            ep=datetime.strptime(end_period, DEFAULT_SERVER_DATE_FORMAT)
            
            bz = StringIO()
            workbook = xlsxwriter.Workbook(bz)
 
            filename = 'Rekap EDC WBH Nasional.xlsx'
 
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
            worksheet.set_row(4, 55)
             
            worksheet.merge_range('A1:H1', 'REKAPITULASI TRANSAKSI ELECTRONIC DATA CAPTURE (EDC)', merge_formats)
            worksheet.write('B3','Start Period :',normal_left_bold)
            worksheet.write('B4', sp.strftime('%d %b %Y'),normal_left)
            worksheet.write('D3', 'End Period :',normal_left_bold)
            worksheet.write('D4', ep.strftime('%d %b %Y'),normal_left) 
            worksheet.write('F3', 'Print Date :',normal_left_bold)
            worksheet.merge_range('F4:G4', today.strftime('%d %b %Y %H:%M'),normal_left) 
             
            worksheet.write('A5', 'DC', normal_bold_border)
            worksheet.write('B5', 'Store Name',normal_bold_border)
            worksheet.write('C5', 'Date', normal_bold_border)
            worksheet.write('D5', 'Trace No.', normal_bold_border)
            worksheet.write('E5', 'Appr. Code', normal_bold_border)
            worksheet.write('F5', 'Bank', normal_bold_border)
            worksheet.write('G5', 'Jumlah', normal_bold_border)
            worksheet.write('H5', 'Total (Akumulasi Transaksi Harian)', normal_bold_border)
            
            worksheet.freeze_panes(8,2)
            
            # how to get data
            row = 1
            number = 1
            total_amount = 0
            amount = 0 
            #query dc
            self.env.cr.execute("""
                    select id, name
                    from res_partner
                    where is_dc = true and active = true
                    order by name asc
                    """)
            result_dc = self.env.cr.fetchall()
            daftar = []
            
            for resDc in result_dc:
                #definisi row awal
                row_awal = row

                #query Store
                self.env.cr.execute("""
                    select pc.id ,pc.name
                    from pos_config as pc
                    join stock_location as sl on sl.id = pc.stock_location_id
                    join res_partner as rp on sl.partner_id = rp.id
                    join res_partner as dcrp on rp.dc_id = dcrp.id
                    where pc.state= 'active' and dcrp.id = %s 
                    """,(resDc[0], ))
                result_store = self.env.cr.fetchall()
                
                nilai_dc = "" #definisi nilai default dc
                for resStore in result_store:
                    #definisi untuk merge range Store
                    selisih_tgl = ep - sp;
                    int_selisih_tgl = np.timedelta64(selisih_tgl, 'D').astype(int)#timedelta to int
                    string_store = 'B'+str(row+5)+':B'+str(row+5+int_selisih_tgl)
                    nilai_dc = resDc[1]
                    #store name column
                    worksheet.merge_range(string_store, resStore[1], normal_center_border)

                    #Query order date,trace no,appr.code,bank,jumlah,akumulasi total
                    for d in self.daterange(sp, ep):
                        var_loop_date = d.date();   
                        self.env.cr.execute("""
                            set datestyle=dmy;
                            select po.date_order as ordat, po.amount_total_rel as amount, aj.type, acbstl.trace_no as traceno, acbstl.appr_code as apprcode
                            from account_bank_statement_line as acbstl
                            join account_bank_statement as acbst on acbst.id = acbstl.statement_id
                            join account_journal as aj on aj.id = acbst.journal_id
                            join pos_order as po on po.id = acbstl.pos_statement_id
                            join pos_session as ps on ps.id = po.session_id
                            join pos_config as pc on pc.id = ps.config_id
                            join stock_location as sl on sl.id = pc.stock_location_id
                            join res_partner as rp on rp.id = sl.partner_id
                            join res_partner as dcrp on rp.dc_id = %s
                            where po.date_order::date = %s and aj.type = 'bank' and pc.name = %s
                            group by po.date_order, po.amount_total_rel, aj.type, acbstl.trace_no, acbstl.appr_code
                            order by po.date_order asc
                            """, (resDc[0], d, resStore[1], ))     
                        result = self.env.cr.dictfetchall()
                        flag = False;
                             
                        for qry in result:
                            str_qry_date = qry['ordat'];#str
                            #memisahkan second float dari data datetime
                            if str_qry_date:
                                hasil_split_datetime= str_qry_date.split(".")[0]
                            var_loop_qry_date = datetime.strptime(hasil_split_datetime , '%Y-%m-%d %H:%M:%S').date();#str to datetime.date
                            
                            if var_loop_qry_date == var_loop_date:
                                total_amount = total_amount + qry['amount']
                                worksheet.write(row+4, 2, var_loop_qry_date.strftime('%d %b %Y'), normal_center_border)
                                worksheet.write(row+4, 3, qry['traceno'], normal_left_border)
                                worksheet.write(row+4, 4, qry['apprcode'], normal_left_border)
                                worksheet.write(row+4, 5, '', normal_left_border)
                                worksheet.write(row+4, 6, qry['amount'], money_format)
                                worksheet.write(row+4, 7, total_amount, money_format)
                                flag = True;
                                row = row + 1;
                        #looping biasa dari tgl
                        if flag == False:
                            worksheet.write(row+4, 2, var_loop_date.strftime('%d %b %Y'), normal_center_border)
                            worksheet.write(row+4, 3, '', normal_left_border)
                            worksheet.write(row+4, 4, '', normal_left_border)
                            worksheet.write(row+4, 5, '', normal_left_border)
                            worksheet.write(row+4, 6, amount, money_format)
                            worksheet.write(row+4, 7, total_amount, money_format)
                            row = row + 1;

                    
                    #sejajar dengan for ke-3
                    total_menotal = 'B'+str(row+5)+':G'+str(row+5)
                    total_semua = 'H'+str(row+5)
                    worksheet.merge_range(total_menotal, 'TOTAL', merge_formats)
                    worksheet.write(total_semua, total_amount, money_format)
                    row = row + 1;
                #definisi row akhir
                row_akhir = row
                #merge range dc
                if nilai_dc:
                    worksheet.merge_range(row_awal+4, 0, row_akhir+3, 0, nilai_dc, normal_center_border)#    
            
            workbook.close()
 
            out = base64.encodestring(bz.getvalue())
            this.write({'state_x':'get', 'data_x':out, 'name': filename})
  
            ir_model_data = self.env['ir.model.data'] 
            bz.close()
            form_res = ir_model_data.get_object_reference("pti_pos_rekap_edc", "report_edc_wbh_nasional")
            form_id = form_res and form_res[1] or False
            return {
                'name': ('Download XLS'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'report.rekap.edc.wbh.nasional',
                'res_id': this.id,
                'view_id': False,
                'views': [(form_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current'
            }
