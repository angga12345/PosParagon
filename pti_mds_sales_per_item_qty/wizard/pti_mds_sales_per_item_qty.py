from openerp import models, fields, api
from cStringIO import StringIO
from datetime import datetime, timedelta
import xlsxwriter
import base64
import time
import pytz


class MdsSalesEachItemReportWizard(models.TransientModel):
    _name = "mds.sales.each.item.qty.report.wizard"

    store = fields.Many2one('pos.config', string="Store",  domain=[('category_shop', '=','shop_in_shop_mds')])
    start_period = fields.Date(string="Start Period")
    end_period = fields.Date(string="End Period")
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    check_all = fields.Boolean('Check')

    @api.multi
    def generate_excel_mds_sales(self):
        form_bc_obj = self.env['pos.order.line']

        start_period = self.start_period
        end_period = self.end_period
        today = datetime.now()
        timezone = pytz.timezone(self._context.get('tz') or 'UTC')
        utc_tz = pytz.utc.localize(today, '%d %b %Y %H:%M').astimezone(timezone)
        sp=datetime.strptime(start_period, '%Y-%m-%d')
        ep=datetime.strptime(end_period, '%Y-%m-%d')
        
        bz = StringIO()
        workbook = xlsxwriter.Workbook(bz)

        filename = 'Laporan Penjualan Per Item/Per Qty.xlsx'

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
        normal_center = workbook.add_format({'valign':'bottom','align':'center'})
        normal_center.set_text_wrap()
        normal_center.set_font_name('Arial')
        normal_center.set_font_size('10')
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
        format_number = workbook.add_format({'valign':'vcenter','align':'right'})
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
        
    
        worksheet = workbook.add_worksheet("report")
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 15)
        
        worksheet.merge_range('A1:C1', 'Laporan Penjualan Per Item Qty', normal_left_bold)
        worksheet.write('B3', 'Start Period:', normal_left_bold)
        worksheet.write('B4', sp.strftime('%d %b %Y'), normal_left_unborder)
        worksheet.write('C3', 'End Period :', normal_left_bold)
        worksheet.write('C4', ep.strftime('%d %b %Y'),normal_left_unborder) 
        worksheet.write('E3', 'Print Date :', normal_left_bold)
        worksheet.write('E4', utc_tz.strftime('%d %b %Y %H:%M'), normal_left_unborder)
        
        worksheet.write('A5', 'No.', normal_bold_border)
        worksheet.write('B5', 'Product', normal_bold_border)
        worksheet.write('C5', 'SKU', normal_bold_border)
        worksheet.write('D5', 'Qty', normal_bold_border)
        # worksheet.write('A7', 'Qty of Product', normal_bold_border)

        self.env.cr.execute("""
          select pproduct.name_template as product, porder.shop_identifier_origin as sku_origin, porder.shop_identifier_period as sku_period,
          sum(pline.qty) as qty
              from pos_order porder join pos_order_line pline on porder.id = pline.order_id 
              join pos_session psession on porder.session_id = psession.id
              join pos_config pconfig on psession.config_id = pconfig.id
              join product_product pproduct on pproduct.id = pline.product_id
          where pconfig.name = %s AND porder.date_order >= %s AND porder.date_order <= %s 
          group by pproduct.name_template, 
                   porder.shop_identifier_origin, 
                   porder.shop_identifier_period
          order by pproduct.name_template
                    """, (self.store.name, start_period+' 00:00:00', end_period+' 23:59:59'))
        
        obj_pos = self.env.cr.fetchall()                         

        row = 0
        number = 1
        inc = 0
        sum_total    = 0.0       

        sku_list = {}
        for pos in obj_pos:
            worksheet.write(row+5 , 0, number, normal_center_border)
            worksheet.write(row+5 , 1, pos[0], normal_left)                        
            sku = pos[1]
            if pos[2]:
                sku = pos[2]  
            #manipulation sku in 8digit
            if len(sku) > 8:
                sku = sku[4:][:-1]          
            worksheet.write(row+5 , 2, sku, normal_center_border)
            worksheet.write(row+5 , 3, pos[3], normal_center_border)            

            sku_list.update({ inc : [sku,pos[3]]})            
            
            number += 1
            row += 1   
            inc += 1                           
        
        sku_set = []
        for sku in sku_list.values():
            sku_set.append(sku[0])

        """get different sku and sum each other"""
        sku_set = list(set(sku_set))
        sku_values = dict()
        for sku_set in sku_set:
            sku_total=0            
            for sku in sku_list.values():                               
                if sku_set == sku[0]:
                    sku_total += sku[1]                
            sku_values.update({sku_set : sku_total})
        
        worksheet.merge_range('A'+str(row+8)+':'+'B'+str(row+8), 'Qty of Product', normal_left_bold)
        for key, value in sku_values.iteritems():
            row += 1
            #manipulation sku in 8digit
            if len(key) > 8:
                key = key[4:][:-1]
            worksheet.merge_range('A'+str(row+8)+':'+'B'+str(row+8), key, normal_left_unborder)
            worksheet.write(row+7, 3, value, normal_center)            
                                            
        workbook.close()

        out = base64.encodestring(bz.getvalue())
        self.write({'state_x':'get', 'data_x':out, 'name': filename})

        ir_model_data = self.env['ir.model.data']
        bz.close()
        form_res = ir_model_data.get_object_reference('pti_mds_sales_per_item_qty', 'mds_sales_each_item_qty_report_wizard_view')
        form_id = form_res and form_res[1] or False
        
        return {
            'name': ('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mds.sales.each.item.qty.report.wizard',
            'res_id': self.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }


