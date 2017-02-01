from openerp import models, fields, api
from cStringIO import StringIO
from datetime import datetime
import xlsxwriter
import base64
import time
import pytz
   
class WbhPosReportWizard(models.TransientModel):
    _name = "wbh.pos.report.wizard"

    start_period = fields.Date(string="Start Period")
    end_period = fields.Date(string="End Period")
    store = fields.Many2one("pos.config", string="Store",
                            domain=[('category_shop', '=', 'stand_alone'),
                                    ('stand_alone_categ', '=', 'wbh')])
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    
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
    
    def _get_data_transaction(self, start_period, end_period, store_id):
#         data_obj = [[]]
        self.env.cr.execute("""
            select ppc.name as categoryname ,pp.name_template as Treatment, pol.price_unit as Price, sum(pol.qty) as Frekuensi, pol.discount as Disc,
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
                    where po.date_order::date BETWEEN %s and %s and pc.id = %s and categ.name = 'WBH'
                    group by ppc.name ,pp.name_template, pol.price_unit, pol.discount, pp.id
                    """,(start_period, end_period, store_id))
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
    
    
    @api.multi
    def generate_excel_wbh_pos(self):
#         for self in self:
        start_period = self.start_period
        end_period = self.end_period
        store = self.store
        today = datetime.now()
        sp=datetime.strptime(start_period, '%Y-%m-%d')
        ep=datetime.strptime(end_period, '%Y-%m-%d')
        
        bz = StringIO()
        workbook = xlsxwriter.Workbook(bz)

        filename = 'Report Treatment ' + store.name +'.xlsx'

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

        worksheet = workbook.add_worksheet("report")
        worksheet.freeze_panes(8,2)
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 40)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 10)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        
        user = self.env['res.users'].browse(self._uid)
        tz = pytz.timezone(user.tz) if user.tz else pytz.utc
        
        todaynow_s = today.strftime('%d %b %Y %H:%M:%S')
        todaynow_f = datetime.strptime(todaynow_s,'%d %b %Y %H:%M:%S')
        todaynow_result = pytz.utc.localize(todaynow_f).astimezone(tz)
        todaynow = datetime.strftime(todaynow_result,'%d %b %Y %H:%M')
        
        
        worksheet.merge_range('A1:H1', 'REKAPITULASI PENJUALAN JASA PERAWATAN WBH', merge_formats)
        worksheet.merge_range('A4:B4','Store Name : '+self.store.name, normal_left_bold)
        worksheet.write('B5','Start Period :',normal_left_bold)
        worksheet.write('B6', sp.strftime('%d %b %Y'),normal_left)
        worksheet.write('C5', 'End Period :',normal_left_bold)
        worksheet.write('C6', ep.strftime('%d %b %Y'),normal_left) 
        worksheet.merge_range('E5:F5', 'Print Date :',normal_left_bold)
        worksheet.merge_range('E6:F6', todaynow,normal_left)
        
        
        worksheet.merge_range('A7:A8', 'No.', normal_bold_border)
        worksheet.merge_range('B7:B8', 'Treatment',normal_bold_border)
        worksheet.merge_range('C7:C8', 'Price', normal_bold_border)
        worksheet.merge_range('D7:D8', 'Frekuensi', normal_bold_border)
        worksheet.merge_range('E7:F7', 'Disc.',normal_bold_border)
        worksheet.write('E8','%', normal_bold_border)
        worksheet.write('F8','Rp', normal_bold_border)
        worksheet.merge_range('G7:G8', 'Total Harga Exclude PPN', normal_bold_border)
        worksheet.merge_range('H7:H8', 'PPN', normal_bold_border)
        
        row = 8
        number = 1
        store_id = self.store.id
        
        start_period = datetime.strptime(start_period,'%Y-%m-%d')
        start_period = start_period.replace(hour=0, minute=0, second=0)
        star_date_result = pytz.utc.localize(start_period).astimezone(tz)
        start_period = datetime.strftime(star_date_result,'%Y-%m-%d %H:%M:%S')
        
        end_period = datetime.strptime(end_period,'%Y-%m-%d')
        end_period = end_period.replace(hour=23, minute=59, second=59)
        end_date_result = pytz.utc.localize(end_period).astimezone(tz)
        end_period = datetime.strftime(end_date_result,'%Y-%m-%d %H:%M:%S')
        
        category_obj = self._get_data_categories()
        product_obj = self._get_data_all_products()
        transaction_obj = self._get_data_transaction(start_period, end_period, store_id)
        
    
        total_frekuensi = 0
        total_subtotal = 0
        total_ppn = 0
        prod_transaksi = []
        for ppc in category_obj:
            categprod = ppc[0]
            worksheet.merge_range('A'+str(row+1)+':B'+str(row+1), categprod, bold_left_category)
            old_row = row
            row += 1    
            sub_subtotal = 0
            sub_ppn = 0
            sub_frekuensi = 0
            
            for transaksi in transaction_obj:
                prod_transaksi.append(transaksi[8])
                if transaksi[0] == ppc[0]:
                    worksheet.write(row, 0, number, normal_center_border)
                    worksheet.write(row, 1, transaksi[1], normal_left_border)
                    worksheet.write(row, 2, transaksi[2], format_number)
                    worksheet.write(row, 3, transaksi[3], format_number)
                    if transaksi[4] == 0:
                        worksheet.write(row, 4, '', format_number)
                        worksheet.write(row, 5, '', format_number)
                    else:
                        worksheet.write(row, 4, transaksi[4], format_number)
                        worksheet.write(row, 5, transaksi[5], format_number)
                    worksheet.write(row, 6, transaksi[6], format_number)
                    worksheet.write(row, 7, transaksi[7], format_number)
                    #Sub
                    sub_frekuensi += transaksi[3]
                    sub_subtotal += transaksi[6]
                    sub_ppn += transaksi[7]
                    
                    #Total
                    total_frekuensi += transaksi[3]
                    total_subtotal += transaksi[6] 
                    total_ppn += transaksi[7]
                    
                    row += 1
                    number += 1
            for prod in product_obj:
                if prod[0] == ppc[0]:
                    if prod[3] not in prod_transaksi:
                        worksheet.write(row, 0, number, normal_center_border)
                        worksheet.write(row, 1, prod[1], normal_left_border)
                        worksheet.write(row, 2, prod[2], format_number)
                        worksheet.write(row, 3, '', format_number)
                        worksheet.write(row, 4, '', format_number)
                        worksheet.write(row, 5, '', format_number)
                        worksheet.write(row, 6, 0, format_number)
                        worksheet.write(row, 7, 0, format_number)

                        row += 1
                        number += 1

                worksheet.write(old_row, 2, '', format_category)
                worksheet.write(old_row, 3, sub_frekuensi, format_category)
                worksheet.write(old_row, 4, '', format_category)
                worksheet.write(old_row, 5, '', format_category)
                worksheet.write(old_row, 6, sub_subtotal, format_category)
                worksheet.write(old_row, 7, sub_ppn, format_category)

                worksheet.write(old_row, 2, '', format_category)
                worksheet.write(old_row, 3, sub_frekuensi, format_category)
                worksheet.write(old_row, 4, '', format_category)
                worksheet.write(old_row, 5, '', format_category)
                worksheet.write(old_row, 6, sub_subtotal, format_category)
                worksheet.write(old_row, 7, sub_ppn, format_category) 

            #Total
            row_total = row
            worksheet.merge_range('A'+str(row_total+1)+':B'+str(row_total+1),'Total',merge_formats_category)
            worksheet.write(row_total , 2, '', format_total)
            worksheet.write(row_total , 3, total_frekuensi, format_total)
            worksheet.write(row_total , 4, '', format_total)
            worksheet.write(row_total , 5, '', format_total)
            worksheet.write(row_total , 6, total_subtotal, format_total)
            worksheet.write(row_total , 7, total_ppn, format_total)

                                         
            worksheet.write(old_row, 2, '', format_category)
            worksheet.write(old_row, 3, sub_frekuensi, format_category)
            worksheet.write(old_row, 4, '', format_category)
            worksheet.write(old_row, 5, '', format_category)
            worksheet.write(old_row, 6, sub_subtotal, format_category)
            worksheet.write(old_row, 7, sub_ppn, format_category) 
            
        #Total
        row_total = row
        worksheet.merge_range('A'+str(row_total+1)+':B'+str(row_total+1),'Total',merge_formats_category)
        worksheet.write(row_total , 2, '', format_total)
        worksheet.write(row_total , 3, total_frekuensi, format_total)
        worksheet.write(row_total , 4, '', format_total)
        worksheet.write(row_total , 5, '', format_total)
        worksheet.write(row_total , 6, total_subtotal, format_total)
        worksheet.write(row_total , 7, total_ppn, format_total)               
          
        workbook.close()

        out = base64.encodestring(bz.getvalue())
        self.write({'state_x':'get', 'data_x':out, 'name': filename})

        ir_model_data = self.env['ir.model.data']
        bz.close()
        form_res = ir_model_data.get_object_reference('pti_wbh_pos_report', 'wbh_pos_report_wizard_view')
        form_id = form_res and form_res[1] or False
        
        return {
            'name': ('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wbh.pos.report.wizard',
            'res_id': self.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }
                