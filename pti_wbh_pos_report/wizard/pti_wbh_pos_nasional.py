from openerp import models, fields, api
from cStringIO import StringIO
from datetime import datetime, timedelta
import xlsxwriter
import base64
import time
import pytz

class WbhPosReportWizard(models.TransientModel):
    _name = "wbh.pos.nasional.report.wizard"

    start_period = fields.Date(string="Start Period")
    end_period = fields.Date(string="End Period")
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    
    def _get_data_dc(self):
#         data_obj = [[]]
        self.env.cr.execute("""
           select id, name
                    from res_partner
                    where is_dc = true and active = true
                    order by id asc
                    """)
        data_obj = self.env.cr.fetchall()
        return data_obj
    
    def _get_data_store(self):
#         data_obj = [[]]
        self.env.cr.execute("""
           select dcrp.id as dc_id, pc.id, pc.name, dcrp.name as name_dc
                    from pos_config as pc
                    join stock_location as sl on sl.id = pc.stock_location_id
                    join res_partner as rp on sl.partner_id = rp.id
                    join res_partner as dcrp on rp.dc_id = dcrp.id
                    where pc.state= 'active' group by pc.id, dcrp.id
                    """)
        data_obj = self.env.cr.fetchall()
        return data_obj
    
    def _get_data_categories(self):
#         data_obj = [[]]
        self.env.cr.execute("""
           select categ.name
                from pos_product_category as wbhcateg
                join pos_product_category as categ on wbhcateg.id = categ.parent_id
                where wbhcateg.name = 'WBH'
                    """)
        data_obj = self.env.cr.fetchall()
        return data_obj
    
    def _get_data_all_products(self):
#         data_obj = [[]]
        self.env.cr.execute("""
            select ppc.name, pp.name_template, pt.list_price, pp.id as product_id from product_template as pt
                    join product_product as pp on pp.product_tmpl_id = pt.id
                    join pos_product_category_product_template_rel as ppcptr on ppcptr.product_template_id = pt.id
                    join pos_product_category as ppc on ppc.id = ppcptr.pos_product_category_id
                    join pos_product_category as categ on categ.id = ppc.parent_id
                    where categ.name = 'WBH'
                    group by ppc.name, pp.name_template, pt.list_price, pp.id
                    """)
        data_obj = self.env.cr.fetchall()
        return data_obj
    
    def _get_data_transaction(self, start_period, end_period):
#         data_obj = [[]]
        self.env.cr.execute("""
           select dc_partner.id as dc_id, dc_partner.name as dc_name, pc.id as store_id, ppc.name as categoryname, pp.name_template as Treatment, pol.price_unit as Price, sum(pol.qty) as Frekuensi, pol.discount as Disc,
                    (pol.discount * pol.price_unit)/100 as Disc_val, sum(pol.price_subtotal_rel) as Subtotal, 
                    round((sum(pol.price_subtotal_rel)*0.1),2) as PPN,
                    pp.id as product_id
                    from pos_order_line as pol
                    join account_tax_pos_order_line_rel as atpolr on atpolr.pos_order_line_id = pol.id
                    join account_tax as at on at.id = atpolr.account_tax_id
                     
                    join product_product as pp on pp.id = pol.product_id
                    join product_template as pt on pt.id = pp.product_tmpl_id
                    join pos_product_category_product_template_rel as ppcptr on ppcptr.product_template_id = pt.id
                    join pos_product_category as ppc on ppc.id = ppcptr.pos_product_category_id
                    join pos_product_category as categ on categ.id = ppc.parent_id
                     
                    join pos_order as po on po.id = pol.order_id
                    join pos_session as ps on ps.id = po.session_id
                    join pos_config as pc on pc.id = ps.config_id
                    join res_partner as rp on pc.partner_id = rp.id
                    join res_partner dc_partner on dc_partner.id = rp.dc_id
                    
                    where po.date_order::date BETWEEN %s and %s
                    and dc_partner.is_dc = true and dc_partner.active = true
                    and pc.category_shop = 'stand_alone' 
                    and pc.state= 'active'
                    and pc.stand_alone_categ = 'wbh' and categ.name = 'WBH'
                    group by ppc.name, pp.name_template, pol.price_unit, pol.discount, pp.id, dc_partner.id, pc.id
                    order by dc_partner.id, pc.id
                    """,(start_period, end_period))
        data_obj = self.env.cr.fetchall()
        return data_obj
    
    @api.multi
    def generate_excel_wbh_pos_nasional(self):
#         for self in self:
        start_period = self.start_period
        end_period = self.end_period
        today = datetime.now()
        sp=datetime.strptime(start_period, '%Y-%m-%d')
        ep=datetime.strptime(end_period, '%Y-%m-%d')
        
        bz = StringIO()
        workbook = xlsxwriter.Workbook(bz)

        filename = 'report_wbh_pos_nasional.xlsx'

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
        bold_left_category.set_font_name('Arial')
        bold_left_category.set_font_size('10')
        bold_left_category.set_border()
        bold_left_category.set_bg_color('#BDC3C7')
        #################################################################################
        merge_formats_category = workbook.add_format({'bold': 1,'align': 'center','valign': 'vcenter',})
        merge_formats_category.set_font_name('Arial')
        merge_formats_category.set_font_size('10')
        merge_formats_category.set_border()
        merge_formats_category.set_bg_color('#99FFFF')
            
        worksheet = workbook.add_worksheet("report")
        worksheet.freeze_panes(7,2)
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 5)
        worksheet.set_column('D:D', 40)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 10)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 15)
        
        user = self.env['res.users'].browse(self._uid)
        tz = pytz.timezone(user.tz) if user.tz else pytz.utc
        
        todaynow_s = today.strftime('%d %b %Y %H:%M:%S')
        todaynow_f = datetime.strptime(todaynow_s,'%d %b %Y %H:%M:%S')
        todaynow_result = pytz.utc.localize(todaynow_f).astimezone(tz)
        todaynow = datetime.strftime(todaynow_result,'%d %b %Y %H:%M')
        
        worksheet.merge_range('A1:J1', 'REKAPITULASI PENJUALAN JASA PERAWATAN WBH (NASIONAL)', merge_formats)
        worksheet.write('A4','Start Period :',normal_left_bold)
        worksheet.write('A5', sp.strftime('%d %b %Y'),normal_left)
        worksheet.write('D4', 'End Period :',normal_left_bold)
        worksheet.write('D5', ep.strftime('%d %b %Y'),normal_left) 
        worksheet.write('E4', 'Print Date :',normal_left_bold)
        worksheet.write('E5', todaynow,normal_left) 
        
        worksheet.merge_range('A6:A7', 'DC', normal_bold_border)
        worksheet.merge_range('B6:B7', 'Store Name', normal_bold_border)
        worksheet.merge_range('C6:C7', 'No.', normal_bold_border)
        worksheet.merge_range('D6:D7', 'Treatment',normal_bold_border)
        worksheet.merge_range('E6:E7', 'Price', normal_bold_border)
        worksheet.merge_range('F6:F7', 'Frekuensi', normal_bold_border)
        worksheet.merge_range('G6:H6', 'Disc.',normal_bold_border)
        worksheet.write('G7','%', normal_bold_border)
        worksheet.write('H7','Rp', normal_bold_border)
        worksheet.merge_range('I6:I7', 'Total', normal_bold_border)
        worksheet.merge_range('J6:J7', 'Ppn', normal_bold_border)
        
        # how to get data
        row = 7
        number = 1
        total = 0
        total_ppn = 0
        row_akhir_category = 0 
        total_frekuensi = 0
        total_subtotal = 0
        total_ppn = 0
        
        start_period = datetime.strptime(start_period,'%Y-%m-%d')
        start_period = start_period.replace(hour=0, minute=0, second=0)
        star_date_result = pytz.utc.localize(start_period).astimezone(tz)
        start_period = datetime.strftime(star_date_result,'%Y-%m-%d %H:%M:%S')
        
        end_period = datetime.strptime(end_period,'%Y-%m-%d')
        end_period = end_period.replace(hour=23, minute=59, second=59)
        end_date_result = pytz.utc.localize(end_period).astimezone(tz)
        end_period = datetime.strftime(end_date_result,'%Y-%m-%d %H:%M:%S')
        
        dc_obj = self._get_data_dc()
        store_obj = self._get_data_store()
        category_obj = self._get_data_categories()
        product_obj = self._get_data_all_products()
        transaction_obj = self._get_data_transaction(start_period, end_period)
        
        
        total_frekuensi = 0
        total_subtotal = 0
        total_ppn = 0
        #query dc
        
        product_save = []
        store_save = []
        
        for dc in dc_obj:
            nilai_dc = ""
            row_awal = row
            for store in store_obj:
                if store[0] == dc[0]:
                    nilai_dc = store[3]
                    worksheet.write(row, 1, store[2], normal_center_border)
                    prod_save = []
                    for categ in category_obj:
                        worksheet.merge_range('C'+str(row+1)+':D'+str(row+1), categ[0], bold_left_category)
                        old_row = row
                        row += 1 
                        sub_frekuensi = 0
                        sub_subtotal = 0
                        sub_ppn = 0
                        for transaction in transaction_obj:
                            prod_save.append(transaction[11])
                            store_save.append(transaction[2])
                            if transaction[0] == dc[0] and transaction[2] == store[1] and transaction[3] == categ[0]:
                                worksheet.write(row, 0, dc[1], normal_center_border)
                                worksheet.write(row, 2, number, normal_center_border)
                                worksheet.write(row, 3, transaction[4], normal_left_border)
                                worksheet.write(row, 4, transaction[5], format_number)
                                worksheet.write(row, 5, transaction[6], format_number)
                                if transaction[7] == 0:
                                    worksheet.write(row, 6, '', format_number)
                                    worksheet.write(row, 7, '', format_number)
                                else:
                                    worksheet.write(row, 6, transaction[7], format_number)
                                    worksheet.write(row, 7, transaction[8], format_number)
                                worksheet.write(row, 8, transaction[9], format_number)
                                worksheet.write(row, 9, transaction[10], format_number)
                                #Sub
                                sub_frekuensi += transaction[6]
                                sub_subtotal += transaction[9]
                                sub_ppn += transaction[10]
                                
                                #Total
                                total_frekuensi += transaction[6]
                                total_subtotal += transaction[9] 
                                total_ppn += transaction[10]
                                
                                row += 1
                                number += 1
                                
                        if store[1] not in store_save:
                            for prod in product_obj:
                                if prod[0] == categ[0]:
                                    worksheet.write(row, 0, dc[1], normal_center_border)
                                    worksheet.write(row, 2, number, normal_center_border)
                                    worksheet.write(row, 3, prod[1], normal_left_border)
                                    worksheet.write(row, 4, prod[2], format_number)
                                    worksheet.write(row, 5, '', format_number)
                                    worksheet.write(row, 6, '', format_number)
                                    worksheet.write(row, 7, '', format_number)
                                    worksheet.write(row, 8, 0, format_number)
                                    worksheet.write(row, 9, 0, format_number)
                                    
                                    row += 1
                                    number += 1
                                    
                        else:
                            for prod in product_obj:
                                if prod[3] not in prod_save:
                                    if prod[0] == categ[0]:
                                        worksheet.write(row, 0, dc[1], normal_center_border)
                                        worksheet.write(row, 2, number, normal_center_border)
                                        worksheet.write(row, 3, prod[1], normal_left_border)
                                        worksheet.write(row, 4, prod[2], format_number)
                                        worksheet.write(row, 5, '', format_number)
                                        worksheet.write(row, 6, '', format_number)
                                        worksheet.write(row, 7, '', format_number)
                                        worksheet.write(row, 8, 0, format_number)
                                        worksheet.write(row, 9, 0, format_number)
                                        
                                        row += 1
                                        number += 1
                                    
                            
                            worksheet.write(old_row, 4, '', format_category)
                            worksheet.write(old_row, 5, sub_frekuensi, format_category)
                            worksheet.write(old_row, 6, '', format_category)
                            worksheet.write(old_row, 7, '', format_category)
                            worksheet.write(old_row, 8, sub_subtotal, format_category)
                            worksheet.write(old_row, 9, sub_ppn, format_category)
                                 
                            worksheet.write(old_row, 4, '', format_category)
                            worksheet.write(old_row, 5, sub_frekuensi, format_category)
                            worksheet.write(old_row, 6, '', format_category)
                            worksheet.write(old_row, 7, '', format_category)
                            worksheet.write(old_row, 8, sub_subtotal, format_category)
                            worksheet.write(old_row, 9, sub_ppn, format_category) 
            
                            
                        #Total Per Sub
                        row_total = row
                        worksheet.merge_range('C'+str(row_total+1)+':D'+str(row_total+1),'Total',merge_formats_category)
                        worksheet.write(row_total , 4, '', format_total)
                        worksheet.write(row_total , 5, total_frekuensi, format_total)
                        worksheet.write(row_total , 6, '', format_total)
                        worksheet.write(row_total , 7, '', format_total)
                        worksheet.write(row_total , 8, total_subtotal, format_total)
                        worksheet.write(row_total , 9, total_ppn, format_total)
             
                                                      
                        worksheet.write(old_row, 4, '', format_category)
                        worksheet.write(old_row, 5, sub_frekuensi, format_category)
                        worksheet.write(old_row, 6, '', format_category)
                        worksheet.write(old_row, 7, '', format_category)
                        worksheet.write(old_row, 8, sub_subtotal, format_category)
                        worksheet.write(old_row, 9, sub_ppn, format_category) 
            
                    row_akhir = row
            row_akhir_dc = row
            
            if nilai_dc:
                    worksheet.merge_range(row_awal, 0, row_akhir-1, 0, nilai_dc, normal_center_border)
                    
        #Total Keseluruhan      
        worksheet.merge_range('A'+str(row_akhir+1)+':D'+str(row_akhir+1),'Total',merge_formats_category)
        
        
        workbook.close()
        out = base64.encodestring(bz.getvalue())
        self.write({'state_x':'get', 'data_x':out, 'name': filename})
        
        ir_model_data = self.env['ir.model.data']
        bz.close()
        form_res = ir_model_data.get_object_reference('pti_wbh_pos_report', 'wbh_pos_nasional_report_wizard_view')
        form_id = form_res and form_res[1] or False
        
        return {
            'name': ('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wbh.pos.nasional.report.wizard',
            'res_id': self.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }