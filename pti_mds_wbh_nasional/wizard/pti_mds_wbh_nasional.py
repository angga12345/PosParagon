from openerp import models, fields, api
from datetime import datetime
from cStringIO import StringIO
import xlsxwriter
import base64

    
class MdsWbhPerStoreReportWizard(models.TransientModel):
    _name = "mds.wbh.nasional.wizard"

    store = fields.Many2one('pos.config', string="Store") #, domain=[('category_shop', '=','shop_in_shop_mds')])
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
        workbook =  xlsxwriter.Workbook(bz)
        
        filename = 'Rekap Penjualan WBH Nasional.xlsx'

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
        normal_center_border = workbook.add_format({'valign':'vcenter','align':'center'})
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
        worksheet.set_column('J:J', 15)
        worksheet.set_column('K:K', 15)
        
        worksheet.merge_range('A1:J1', 'REKAPITULASI SETORAN PENJUALAN WBH NASIONAL', normal_bold) #dynamic value for store name
        worksheet.write('A3','Start Period :', normal_left_unborder_bold)
        worksheet.write('A4', sp.strftime('%d %b %Y'), normal_left_unborder)
        worksheet.write('C3', 'End Period :', normal_left_unborder_bold)
        worksheet.write('C4', ep.strftime('%d %b %Y'),normal_left_unborder) 
        worksheet.write('E3', 'Print Date :', normal_left_unborder_bold)
        worksheet.write('E4', today.strftime('%d %b %Y'), normal_left_unborder)         
        
        worksheet.merge_range('A5:A6','DC',normal_bold_border)
        worksheet.merge_range('B5:B6','Store Name', normal_bold_border)
        worksheet.merge_range('C5:C6','Date', normal_bold_border)
        worksheet.merge_range('D5:E5','Penjualan', normal_bold_border)
        worksheet.write('D6','Product.', normal_bold_border)
        worksheet.write('E6','Treatment', normal_bold_border)
        worksheet.merge_range('F5:F6','Promo Disc.', normal_bold_border)
        worksheet.merge_range('G5:G6','Voucher', normal_bold_border)
        worksheet.merge_range('H5:H6','EDC', normal_bold_border)
        worksheet.merge_range('I5:I6','Modal Kembalian', normal_bold_border)
        worksheet.merge_range('J5:J6','Perhitungan Nominal Setor', normal_bold_border)
        worksheet.freeze_panes(9,2)
        

        ################################# Set Interval Date #################################        
        from datetime import timedelta, date
        
        def daterange(start_date, end_date):
            for n in range(int((datetime.strptime(end_date,'%Y-%m-%d')-datetime.strptime(start_date,'%Y-%m-%d')).days)+1):
                yield datetime.strptime(start_date,'%Y-%m-%d') + timedelta(n)

        ############################################## LOOPING DC & NAMA TOKO ###############################################
        self.env.cr.execute("""
            select dcpartner.name as dc, pbrand.name as brand, pconfig.name as shop, ptemplate.type, date(porder.date_order),
                    coalesce(sum(pline.price_subtotal_rel),0) as total
                    from pos_order porder join pos_order_line pline on porder.id = pline.order_id 
                        join pos_session psession on porder.session_id = psession.id
                        join pos_config pconfig on psession.config_id = pconfig.id
                        join product_product pproduct on pproduct.id = pline.product_id
                        join stock_location slocation on slocation.id = pconfig.stock_location_id
                        join res_partner rpartner on rpartner.id = slocation.partner_id
                        join res_partner dcpartner on rpartner.dc_id = dcpartner.id 
                        join product_brand pbrand on pbrand.id = pconfig.tags
                        join product_template ptemplate on pproduct.product_tmpl_id = ptemplate.id
                    where porder.date_order >= %s AND porder.date_order <= %s
                    group by date(porder.date_order), ptemplate.type, pbrand.name, dcpartner.name, pconfig.name
                    order by dcpartner.name, pbrand.name, pconfig.name asc
                    """, (self.start_period+' 00:00:00', end_period+' 23:59:59'))
        brand = {}
        q1 = self.env.cr.fetchall()
        for q in q1:               
            if q[0] in brand:
                if q[1] in brand[q[0]]:
                    if q[2] in brand[q[0]][q[1]]:
                        brand[q[0]][q[1]][q[2]].append(q[4])
                    else:
                        brand[q[0]][q[1]][q[2]] = []
                else:
                    brand[q[0]][q[1]] = {}
            else:
                brand[q[0]] = {}
                brand[q[0]][q[1]] = {}
                brand[q[0]][q[1]][q[2]] = []
                brand[q[0]][q[1]][q[2]].append(q[4])

        total_prod = 0
        total_serv = 0
        tot_total_prod = 0
        tot_total_serv = 0
        row = 0
        x = 0
        rowx = 6
        first_row = 6
        for key, value in brand.iteritems():         
            for k, v in value.iteritems():
                for k1, v1 in v.iteritems():

                    ########################## query for get Product Price (Product which type is stockable and service) ############################
                    self.env.cr.execute("""
                    SELECT DISTINCT temp.date_order as date_order, temp.type, sum(temp.price)
                    FROM
                            (SELECT  date(porder.date_order) as date_order,
                                     ptemplate.type as type,
                                     sum(ptemplate.list_price) as price                         
                            FROM pos_order porder join pos_order_line pline on porder.id = pline.order_id 
                                    join pos_session psession on porder.session_id = psession.id                                        
                                    join pos_config pconfig on psession.config_id = pconfig.id
                                    join product_product pproduct on pproduct.id = pline.product_id
                                    join product_template ptemplate on ptemplate.id=pproduct.product_tmpl_id            
                            WHERE pconfig.name = %s AND porder.date_order >= %s AND porder.date_order <= %s
                            GROUP BY porder.date_order, ptemplate.type
                            ORDER BY porder.date_order ASC) as temp
                    GROUP BY temp.date_order, temp.type
                    ORDER BY temp.date_order ASC                    
                    """, (k1, start_period+' 00:00:00', end_period+' 23:59:59'))
                    pos_product_obj = self.env.cr.fetchall()     
                    
                    product_type_obj={} 
                    treatment_type_obj={} 
                    for prod in pos_product_obj:
                        date=prod[0]
                        type_prod=prod[1]
                        product=prod[2]
                          
                        if type_prod=='product':
                            product_type_obj.update({date:product})
                        elif type_prod=='service':
                            treatment_type_obj.update({date:product})

                    ################################# query for Promo Disc #################################
                    self.env.cr.execute("""
                    SELECT DISTINCT temp.date_order, sum(temp.discount)
                    FROM
                            (SELECT  date(porder.date_order) as date_order,
                                     sum(pline.discount) as Discount
                            FROM pos_order porder join pos_order_line pline on porder.id = pline.order_id 
                                    join pos_session psession on porder.session_id = psession.id
                                    join pos_config pconfig on psession.config_id = pconfig.id
                                    join product_product pproduct on pproduct.id = pline.product_id
                            WHERE pconfig.name = %s AND porder.date_order >= %s AND porder.date_order <= %s 
                            GROUP BY porder.date_order
                            ORDER BY porder.date_order ASC) as temp
                    GROUP BY temp.date_order
                    ORDER BY temp.date_order ASC
                    """, (k1, start_period+' 00:00:00', end_period+' 23:59:59'))        
                    pos_discount_obj = self.env.cr.fetchall()
                    
                    promo_discount_obj={}
                    for pos in pos_discount_obj:
                        date=pos[0]
                        discount=pos[1]
                        
                        promo_discount_obj.update({date:discount})                            

                    ################################# query for get Voucher Price #################################
                    self.env.cr.execute("""
                    SELECT DISTINCT temp.date_order as date_order, sum(temp.price)
                    FROM
                            (SELECT  date(porder.date_order) as date_order,
                                     sum(ptemplate.list_price) as price
                            FROM pos_order porder join pos_order_line pline on porder.id = pline.order_id 
                                    join pos_session psession on porder.session_id = psession.id                                        
                                    join pos_config pconfig on psession.config_id = pconfig.id
                                    join product_product pproduct on pproduct.id = pline.product_id
                                    join product_template ptemplate on ptemplate.id=pproduct.product_tmpl_id            
                            WHERE pconfig.name = %s AND porder.date_order >= %s AND porder.date_order <= %s AND ptemplate.voucher=True
                            GROUP BY porder.date_order
                            ORDER BY porder.date_order ASC) as temp
                    GROUP BY temp.date_order   
                    ORDER BY temp.date_order ASC                    
                    """, (k1, start_period+' 00:00:00', end_period+' 23:59:59'))
                    pos_voucher_obj = self.env.cr.fetchall()  
                    
                    voucher_obj={}
                    for voucher_prod in pos_voucher_obj:
                        date=voucher_prod[1]
                        voucher=voucher_prod[1]
                        
                        voucher_obj.update({date:voucher})
                                
                    ################################# query for get Modal Kembalian #################################
                    self.env.cr.execute("""
                    SELECT DISTINCT temp.date_order, sum(temp.starting_balance)
                    FROM
                            (SELECT  date(porder.date_order) as date_order,
                                     sum(paccount.balance_start) as starting_balance                   
                            FROM pos_order porder join pos_order_line pline on porder.id = pline.order_id 
                                    join pos_session psession on porder.session_id = psession.id
                                    join account_bank_statement paccount on paccount.pos_session_id = psession.id
                                    join pos_config pconfig on psession.config_id = pconfig.id
                            WHERE pconfig.name = %s AND porder.date_order >= %s AND porder.date_order <= %s 
                            GROUP BY porder.date_order, paccount.balance_start
                            ORDER BY porder.date_order ASC) as temp
                    GROUP BY temp.date_order
                    ORDER BY temp.date_order ASC
                    """, (k1, start_period+' 00:00:00', end_period+' 23:59:59'))        
                    pos_balance_obj = self.env.cr.fetchall()
                    
                    balance_obj={}
                    for balance in pos_balance_obj:
                        date=balance[0]
                        modal_kembalian=balance[1]
                        
                        balance_obj.update({date:modal_kembalian})
                            
                    ################################# Set Default Border and Value = 0 ################################# 
                    row=0
                    list_date=daterange(start_period,end_period)
                    for idx ,dates in enumerate(list_date, first_row):
                        dates=datetime.strptime(str(dates), '%Y-%m-%d %H:%M:%S').strftime('%d %b %Y')
                        worksheet.write(idx, 0, '', normal_center)
                        worksheet.write(idx, 1, '', normal_center)
                        worksheet.write(idx, 2, dates, normal_center)
                        worksheet.write(idx, 3, '0', normal_center)
                        worksheet.write(idx, 4, '0', normal_center)
                        worksheet.write(idx, 5, '0', normal_center)
                        worksheet.write(idx, 6, '0', normal_center)
                        worksheet.write(idx, 7, '0', normal_center)
                        worksheet.write(idx, 8, '0', normal_center)
                        nominal_setor= '{=SUM(D'+str(idx+1)+':E'+str(idx+1)+')-SUM(F'+str(idx+1)+':I'+str(idx+1)+')}'  
                        worksheet.write_formula(idx, 9, nominal_setor, normal_center)
                        row+=1

                    ################################# Fill Report (Override) ##########################################
                    row=0
                    list_date=daterange(start_period,end_period)
                    for idx ,dates in enumerate(list_date, first_row):
                        dates=datetime.strptime(str(dates), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                                   
                        for dates_type, price_prod in product_type_obj.iteritems():
                            if dates == dates_type:
                                worksheet.write(idx, 3, price_prod, format_number) 

                        for dates_type, price_treatment in treatment_type_obj.iteritems():
                            if dates == dates_type:
                                worksheet.write(idx, 4, price_treatment, format_number) 
                        
                        for dates_discount, price in promo_discount_obj.iteritems():
                            if dates == dates_discount:
                                if price == float(0):
                                    worksheet.write(idx, 5, "{:.0f}".format(price), normal_center)
                                else:
                                    worksheet.write(idx, 5, price, format_number) 
                 
                        for dates_voucher, price in voucher_obj.iteritems():
                            if dates == dates_voucher:
                                if price == float(0):
                                    worksheet.write(idx, 6, "{:.0f}".format(price), normal_center) 
                                else:
                                    worksheet.write(idx, 6, price, format_number) 

                        for dates_balance, price in balance_obj.iteritems():
                            if dates == dates_balance:
                                if price == float(0):
                                    worksheet.write(idx, 8, "{:.0f}".format(price), format_number)
                                else:
                                    worksheet.write(idx, 8, price, format_number)            
                        row+=1
                        
                    ################################# SUM Total per Column #################################
                    last_row=idx
                    row_total=idx+1
                    worksheet.merge_range(row_total, 1, row_total, 2, "TOTAL", normal_bold_border)
                    worksheet.write_formula(row_total, 3, "{=SUM(D"+str(first_row+1)+":D"+str(last_row+1)+")}", format_number_total)
                    worksheet.write_formula(row_total, 4, "{=SUM(E"+str(first_row+1)+":E"+str(last_row+1)+")}", format_number_total)
                    worksheet.write_formula(row_total, 5, "{=SUM(F"+str(first_row+1)+":F"+str(last_row+1)+")}", format_number_total)
                    worksheet.write_formula(row_total, 6, "{=SUM(G"+str(first_row+1)+":G"+str(last_row+1)+")}", format_number_total)
                    worksheet.write_formula(row_total, 7, "{=SUM(H"+str(first_row+1)+":H"+str(last_row+1)+")}", format_number_total)
                    worksheet.write_formula(row_total, 8, "{=SUM(I"+str(first_row+1)+":I"+str(last_row+1)+")}", format_number_total)
                    worksheet.write_formula(row_total, 9, "{=SUM(J"+str(first_row+1)+":J"+str(last_row+1)+")}", format_number_total)    
                    ###########################################################################################

                    worksheet.merge_range(first_row, 1, row_total-1, 1, k1, normal_center_border)
                    first_row=first_row+row+1

            worksheet.merge_range(rowx, 0, row_total, 0, key, normal_center_border)
            rowx=row_total+1
            
        workbook.close()
        
        out = base64.encodestring(bz.getvalue())
        self.write({'state_x':'get', 'data_x':out, 'name': filename})

        ir_model_data = self.env['ir.model.data']
        bz.close()
        form_res = ir_model_data.get_object_reference('pti_mds_wbh_nasional', 'mds_wbh_nasional_wizard_view')
        form_id = form_res and form_res[1] or False
        
        return {
            'name': ('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mds.wbh.nasional.wizard',
            'res_id': self.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }