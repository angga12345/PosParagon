from openerp import models, fields, api
from datetime import datetime
from cStringIO import StringIO
import xlsxwriter
import base64
import time
    
class MdsWbhStoreReportWizard(models.TransientModel):
    _name = "mds.wbh.store.report.wizard"

    store = fields.Many2one('pos.config', string="Store", domain=[('category_shop', '=','stand_alone')])
    start_period = fields.Date(string="Start Period")
    end_period = fields.Date(string="End Period")
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    check_all=fields.Boolean('Check')
    
    @api.multi
    def generate_excel_mds_wbh(self):
        start_period = self.start_period
        end_period = self.end_period
        today = datetime.now()
        sp=datetime.strptime(start_period, '%Y-%m-%d')
        ep=datetime.strptime(end_period, '%Y-%m-%d')  
        
        bz = StringIO()
        workbook = xlsxwriter.Workbook(bz)
        
        filename = 'Rekap Penjualan Bulanan '+str(self.store.name)+' .xlsx'
        
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
        normal_center_border = workbook.add_format({'valign':'bottom','align':'center'})
        normal_center_border.set_text_wrap()
        normal_center_border.set_font_name('Arial')
        normal_center_border.set_font_size('10')
        normal_center_border.set_border()
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
        format_number = workbook.add_format({'valign':'vcenter','align':'center'})
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
        #################################################################################
        format_number_total = workbook.add_format({'bold': 1,'valign':'vcenter','align':'center'})
        format_number_total.set_num_format('#,##0.00')
        format_number_total.set_font_name('Arial')
        format_number_total.set_font_size('10')
        format_number_total.set_border()        
             
        worksheet = workbook.add_worksheet("report")
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 20)
        worksheet.set_column('K:K', 20)
        
        worksheet.merge_range('A1:H1', 'REKAPITULASI SETORAN PENJUALAN '+str(self.store.name), normal_bold) #dynamic value for store name
        worksheet.merge_range('A2:B3', 'Store Name: '+str(self.store.name), normal_left_unborder_bold) #dynamic value for store name
        worksheet.write('B4','Start Period :', normal_left_unborder_bold)
        worksheet.write('B5', sp.strftime('%d %b %Y'), normal_left_unborder)
        worksheet.write('D4', 'End Period :', normal_left_unborder_bold)
        worksheet.write('D5', ep.strftime('%d %b %Y'),normal_left_unborder) 
        worksheet.write('F4', 'Print Date :', normal_left_unborder_bold)
        worksheet.write('F5:F5', today.strftime('%d %b %Y %H:%M'), normal_left_unborder)         
        
        worksheet.merge_range('A6:A7','Date',normal_bold_border)
        worksheet.merge_range('B6:C6','Penjualan', normal_bold_border)
        worksheet.write('B7','Product', normal_bold_border)
        worksheet.write('C7','Treatment', normal_bold_border)
        worksheet.merge_range('D6:D7','Promo Disc.', normal_bold_border)
        worksheet.merge_range('E6:E7','Voucher', normal_bold_border)
        worksheet.merge_range('F6:F7','EDC', normal_bold_border)
        worksheet.merge_range('G6:G7','Modal Kembalian', normal_bold_border)
        worksheet.merge_range('H6:H7','Perhitungan \n Nominal Setor', normal_bold_border)
        worksheet.freeze_panes(9,2)
        
        ################################# Set Interval Date #################################        
        from datetime import timedelta, date
        
        def daterange(start_date, end_date):
            for n in range(int((datetime.strptime(end_date,'%Y-%m-%d')-datetime.strptime(start_date,'%Y-%m-%d')).days)+1):
                yield datetime.strptime(start_date,'%Y-%m-%d') + timedelta(n)
        
        ################################# Set Default Border and Value = 0 ################################# 
        list_date=daterange(start_period,end_period)
        row=0 
        for dates in list_date:
            row+=1
            date=datetime.strptime(str(dates), '%Y-%m-%d %H:%M:%S').strftime('%d %b %Y')
            worksheet.write(row+6, 0, date, normal_center)
            worksheet.write(row+6, 1, '0', normal_center)
            worksheet.write(row+6, 2, '0', normal_center)
            worksheet.write(row+6, 3, '0', normal_center)
            worksheet.write(row+6, 4, '0', normal_center)
            worksheet.write(row+6, 5, '0', normal_center)
            worksheet.write(row+6, 6, '0', normal_center)
            nominal_setor= '{=SUM(B'+str(row+7)+':C'+str(row+7)+')-SUM(D'+str(row+7)+':G'+str(row+7)+')}'  
            worksheet.write_formula(row+6, 7, nominal_setor, normal_center)      
                                         
        ################################# query without discount 1 n 2 (Product which type is stockable and service) #################################
        
        self.env.cr.execute("""
        select
            date (pos.date_order),
            sum(case when pt.type = 'product' then pol.price_unit else 0 end) as product,
            sum(case when pt.type = 'service' then pol.price_unit  else 0 end) as service,
            sum(pol.price_unit - (pol.price_unit * (case when pol.discount <> 0 then pol.discount / 100 else 1 end))) as discount,
            sum(case when pt.voucher = true then abs(pt.list_price) else 0 end) as voucher,
            sum(paccount.balance_start) as modal_kembalian
        from pos_order  pos
            left join pos_order_line pol on pol.order_id = pos.id
            left join product_product p on p.id = pol.product_id
            left join product_template pt on pt.id = p.product_tmpl_id
            left join pos_session s on s.id = pos.session_id
            left join account_bank_statement paccount on s.id = paccount.pos_session_id
            left join account_journal pjournal on pjournal.id = paccount.journal_id
        where pjournal.type = 'cash'
            and date(pos.date_order) <= %s
            and date(pos.date_order) >= %s
        group by 1
        order by 1
        """            
            , (start_period, end_period))
        base_report = self.env.cr.fetchall()
        
        
        ############################# Get Discount MAXIMUM REWARD ############################
        
        self.env.cr.execute("""
            select
                pos.date_order, sum(pos.max_reward_value)
            from pos_order  pos
            where date(pos.date_order) <= %s
                and date(pos.date_order) >= %s
            group by pos.date_order
        """, (start_period, end_period))
        max_r = self.env.cr.fetchall()
        mr = []
        for m_r in max_r:
            mr.append(m_r[1])
        
        ######################################################################################
        ###############################Get Discount SPECIAL PRICE ###########################
        
        self.env.cr.execute(
            """
            select
                pos.date_order, sum(pol.qty * pol.price_unit) - pos.special_price
            from pos_order pos
                left join pos_order_line pol on pol.order_id = pos.id
            where date(pos.date_order) <= %s
                and date(pos.date_order) >= %s
            group by pos.date_order,  pos.special_price
            """, (start_period, end_period))
        sp_price = self.env.cr.fetchall()
        spp = []
        for sp_p in sp_price:
            spp.append(sp_p[1])
        ######################################################################################
        row = 7
        i = 0
        for data in base_report:
            datesql = datetime.strptime(str(data[0]), '%Y-%m-%d').strftime('%Y-%m-%d')
            
            if datesql <= ep.strftime('%Y-%m-%d') and datesql >= sp.strftime('%Y-%m-%d'):
                print('going here')
                worksheet.write(row, 1, data[1], format_number)#product
                worksheet.write(row, 2, data[2], format_number)#treatment
                worksheet.write(row, 3, data[3] + spp[1] + mr[1], format_number)#promo disc
                worksheet.write(row, 4, data[4], format_number)#voucher
    #             worksheet.write(row, 5, 'limo', format_number)#edc
                worksheet.write(row, 6, data[5], format_number)#modal kembalian
                row += 1
                i += 1
                
        ################################# SUM Total per Column #################################
        last_row=row
        row_total=row
        worksheet.write(row_total, 0, "TOTAL", normal_bold_border)
        worksheet.write_formula(row_total, 1, "{=SUM(B8:B"+str(last_row)+")}", format_number_total)
        worksheet.write_formula(row_total, 2, "{=SUM(C8:C"+str(last_row)+")}", format_number_total)
        worksheet.write_formula(row_total, 3, "{=SUM(D8:D"+str(last_row)+")}", format_number_total)
        worksheet.write_formula(row_total, 4, "{=SUM(E8:E"+str(last_row)+")}", format_number_total)
        worksheet.write_formula(row_total, 5, "{=SUM(F8:F"+str(last_row)+")}", format_number_total)
        worksheet.write_formula(row_total, 6, "{=SUM(G8:G"+str(last_row)+")}", format_number_total)
        worksheet.write_formula(row_total, 7, "{=SUM(H8:H"+str(last_row)+")}", format_number_total)    
            
        ###########################################################################################
        
        workbook.close()
        
        out = base64.encodestring(bz.getvalue())
        self.write({'state_x':'get', 'data_x':out, 'name': filename})

        ir_model_data = self.env['ir.model.data']
        bz.close()
        form_res = ir_model_data.get_object_reference('pti_mds_wbh_store', 'mds_wbh_store_report_wizard_view')
        form_id = form_res and form_res[1] or False
        
        return {
            'name': ('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mds.wbh.store.report.wizard',
            'res_id': self.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }
        