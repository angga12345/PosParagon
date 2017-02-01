from openerp import models, fields, api
from cStringIO import StringIO
from datetime import datetime, timedelta
import xlsxwriter
import base64
import time
import pytz


class MdsSalesEachItemReportWizard(models.TransientModel):
    _name = "mds.sales.each.item.report.wizard"

    store = fields.Many2one('pos.config', string="Store", domain=[('category_shop', '=','shop_in_shop_mds')])
    start_period = fields.Date(string="Start Period")
    end_period = fields.Date(string="End Period")
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    check_all=fields.Boolean('Check')

    def _get_data_product(self, store_id, start_date, end_date):
        self.env.cr.execute("""
            select pproduct.name_template as product,
                case
                    when porder.shop_identifier_period is not null and porder.shop_identifier_period != '' then porder.shop_identifier_period
                    when porder.shop_identifier_origin is not null then porder.shop_identifier_origin
                end as sku,
                round(pline.price_unit,2) as Price,
                sum(pline.qty) as Qty,
                pline.discount as disc,
                round((pline.price_unit * sum(pline.qty)) * (pline.discount / 100),2) as Rp,
                round((pline.price_unit * sum(pline.qty)) - ((pline.price_unit * sum(pline.qty)) * (pline.discount / 100)),2) as Total,
                round(((pline.price_unit * sum(pline.qty)) - ((pline.price_unit * sum(pline.qty)) * (pline.discount / 100))) * 0.1,2) as Ppn
                from pos_order_line pline 
                join pos_order porder on porder.id = pline.order_id 
                join product_product pproduct on pproduct.id = pline.product_id
                join product_template ptemplate on pproduct.product_tmpl_id = ptemplate.id
                join pos_session psession on psession.id = porder.session_id
                join pos_config pconfig on pconfig.id = psession.config_id
                where pconfig.id = %s and porder.date_order >= %s and porder.date_order <= %s
                group by pproduct.name_template, 
                    porder.shop_identifier_period, 
                    pline.price_unit, pline.qty, 
                    pline.discount, 
                    pline.price_unit,
                    porder.shop_identifier_origin,
                    porder.shop_identifier_period
                order by pproduct.name_template asc""", (store_id, start_date, end_date))
        data_obj = self.env.cr.fetchall()
        return data_obj

    def _get_data_max_rewards(self, store_id, start_date, end_date):
        self.env.cr.execute("""
            select po.max_reward_value as reward,
                case
                    when po.shop_identifier_period is not null and po.shop_identifier_period != '' then po.shop_identifier_period
                    when po.shop_identifier_origin is not null then po.shop_identifier_origin
                end as sku, lreward.name
                from pos_order po
                join pos_session ps on ps.id = po.session_id
                join pos_config pc on pc.id = ps.config_id
                join loyalty_reward lreward on lreward.id = po.loyalty_reward_id
                join loyalty_program lprogram on lprogram.id = lreward.loyalty_program_id
                where pc.id = %s and po.date_order >= %s and po.date_order <= %s
                AND po.is_max_reward = True
                """, (store_id, start_date, end_date))
        data_obj = self.env.cr.fetchall()
        return data_obj
    
    def _get_data_special_price(self, store_id, start_date, end_date):
        self.env.cr.execute("""
            select sum(pol.price_subtotal_incl_rel / (select count(rel.product_template_id)
                from pos_product_category_product_template_rel rel 
                where rel.product_template_id = prel.product_template_id)) - po.special_price as DiscountSpecialPrice,
                case
                    when po.shop_identifier_period is not null and po.shop_identifier_period != '' then po.shop_identifier_period
                    when po.shop_identifier_origin is not null then po.shop_identifier_origin
                end as sku, lreward.name
                from pos_order_line pol join pos_order po on po.id = pol.order_id
                join pos_session ps on ps.id = po.session_id
                join pos_config pc on pc.id = ps.config_id
                join product_product pp on pol.product_id = pp.id
                join loyalty_reward lreward on lreward.id = po.loyalty_reward_id
                join loyalty_program lprogram on lprogram.id = lreward.loyalty_program_id,
                pos_product_category_product_template_rel prel,
                pos_product_category pcategory
                where pol.is_special_price = True
                AND pc.id = %s
                AND prel.product_template_id = pp.product_tmpl_id
                AND pcategory.id = prel.pos_product_category_id
                AND po.date_order >= %s and po.date_order <= %s
                group by po.id, po.shop_identifier_period, lreward.name
                    """, (store_id, start_date, end_date))
        data_obj = self.env.cr.fetchall()
        return data_obj

    @api.multi
    def generate_excel_mds_sales(self):
        today = datetime.now()
        timezone = pytz.timezone(self._context.get('tz') or 'UTC')
        utc_tz = pytz.utc.localize(today, '%d %b %Y %H:%M').astimezone(timezone)
        form_bc_obj = self.env['pos.order.line']
        start_period = self.start_period
        end_period = self.end_period
        today = datetime.now()
        sp=datetime.strptime(start_period, '%Y-%m-%d')
        ep=datetime.strptime(end_period, '%Y-%m-%d')
        
        bz = StringIO()
        workbook = xlsxwriter.Workbook(bz)

        filename = 'Laporan Penjualan by Item / by  SKU per Rupiah''.xlsx'

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
        worksheet.set_column('B:B', 55)
        worksheet.set_column('C:C', 12)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 6)
        worksheet.set_column('F:F', 4)
        worksheet.set_column('G:G', 14)
        worksheet.set_column('H:H', 16)
        worksheet.set_column('I:I', 14)

        worksheet.merge_range('A1:C1', 'Laporan Penjualan by Item / by  SKU per Rupiah', normal_left_bold)
        worksheet.merge_range('A2:C2','Nama Store : '+self.store.name, normal_left_bold)
        worksheet.write('B3','Start Period :', normal_left_unborder)
        worksheet.write('B4', sp.strftime('%d %b %Y'), normal_left_unborder)
        worksheet.write('D3', 'End Period :', normal_left_unborder)
        worksheet.write('D4', ep.strftime('%d %b %Y'),normal_left_unborder) 
        worksheet.write('H3', 'Print Date :', normal_left_unborder)
        worksheet.write('H4', utc_tz.strftime('%d %b %Y %H:%M'), normal_left_unborder)
        
        worksheet.merge_range('A6:A7', 'No.', normal_bold_border)
        worksheet.merge_range('B6:B7', 'Product', normal_bold_border)
        worksheet.merge_range('C6:C7', 'SKU', normal_bold_border)
        worksheet.merge_range('D6:D7', 'Price', normal_bold_border)
        worksheet.merge_range('E6:E7', 'Qty', normal_bold_border)
        worksheet.merge_range('F6:G6', 'Discount', normal_bold_border)
        worksheet.write('F7', '%', normal_bold_border)
        worksheet.write('G7', 'Rp', normal_bold_border)
        worksheet.merge_range('H6:H7', 'Total', normal_bold_border)
        worksheet.merge_range('I6:I7', 'Ppn', normal_bold_border)
        # worksheet.freeze_panes(6,0)

        row = 0
        number = 1
        inc = 0
        sum_total    = 0.0
        sum_ppn      = 0.0
        sum_discount = 0.0
        sum_all_ppn = 0.0
        total_all_sales  = 0.0
        store_id = self.store.id
        
        obj_pos = self._get_data_product(store_id, start_period+' 00:00:00', end_period+' 23:59:59')
        obj_pos_max_reward = self._get_data_max_rewards(store_id, start_period+' 00:00:00', end_period+' 23:59:59')
        obj_pos_special_price = self._get_data_special_price(store_id, start_period+' 00:00:00', end_period+' 23:59:59')

        sku_list = {}
        for pos in obj_pos:
            worksheet.write(row+7 , 0, number, normal_center)
            worksheet.write(row+7 , 1, pos[0], normal_left)                        
            #manipulation sku in 8digit
            sku = pos[1]
            if len(sku) > 8:
                sku = sku[4:][:-1]
            worksheet.write(row+7 , 2, sku, format_number)
            worksheet.write(row+7 , 3, pos[2], normal_center)
            worksheet.write(row+7 , 4, pos[3], format_number)            
            if pos[4]==0:
                worksheet.write(row+7 , 5, '', normal_center)
                worksheet.write(row+7 , 6, '', format_number)        
            else:
                worksheet.write(row+7 , 5, pos[4], normal_center)
                worksheet.write(row+7 , 6, pos[5], format_number)                                    
                sum_discount += pos[5]                                      
            worksheet.write(row+7 , 7, pos[6], format_number)
            worksheet.write(row+7 , 8, pos[7], format_number)
            sku_list.update({ inc : [sku,pos[6]]}) 

            sum_total    += pos[6]
            sum_ppn      += pos[7]
                        
            number += 1
            row += 1

            inc += 1
            
        for max_reward in obj_pos_max_reward:
            worksheet.write(row+7 , 0, number, normal_center)
            worksheet.write(row+7 , 1, 'Cashback ' + max_reward[2], normal_left)
            sku = max_reward[1]
            if len(sku) > 8:
                sku = sku[4:][:-1]
            worksheet.write(row+7 , 2, sku, format_number)
            worksheet.write(row+7 , 3, max_reward[0], normal_center)            
            worksheet.write(row+7 , 4, 1, format_number)
            worksheet.write(row+7 , 5, '', format_number)                                    
            worksheet.write(row+7 , 6, '', format_number)  
            worksheet.write(row+7 , 7, -max_reward[0], format_number)
            worksheet.write(row+7 , 8, '', format_number)
            sku_list.update({inc: [sku, -max_reward[0]]})

            sum_total    -= max_reward[0]
            sum_discount += max_reward[0]
                                   
            number += 1
            row += 1
            inc += 1

        for special in obj_pos_special_price:
            worksheet.write(row+7 , 0, number, normal_center)
            worksheet.write(row+7 , 1, 'Cashback Special Price '+ special[2], normal_left)
            sku = special[1]
            if len(sku) > 8:
                sku = sku[4:][:-1]
            worksheet.write(row+7 , 2, sku, format_number)
            worksheet.write(row+7 , 3, special[0], normal_center)            
            worksheet.write(row+7 , 4, 1, format_number)
            worksheet.write(row+7 , 5, '', format_number)                                    
            worksheet.write(row+7 , 6, '', format_number)  
            worksheet.write(row+7 , 7, -special[0], format_number)
            worksheet.write(row+7 , 8, '', format_number)
            sku_list.update({inc: [sku, -special[0]]})

            sum_total    -= special[0]
            sum_discount += special[0]
                        
            number += 1
            row += 1
            inc += 1

        worksheet.merge_range('A'+str(row+8)+':'+'E'+str(row+8), 'TOTAL', normal_bold_border)
        worksheet.write(row+7 , 5, '', format_number)
        worksheet.write(row+7 , 6, sum_discount, format_number)
        worksheet.write(row+7 , 7, sum_total, format_number_bold)  
        worksheet.write(row+7 , 8, sum_ppn, format_number_bold)

        sum_all_ppn  += sum_ppn
        sku_set = []
        for sku in sku_list.values():
            sku_set.append(sku[0])
        sku_set = list(set(sku_set))
        sku_values = dict()
        for  sku_set in sku_set:
            sku_total=0            
            for sku in sku_list.values():
                if sku_set == sku[0]:
                    sku_total += sku[1]
            sku_values.update({sku_set : sku_total})
        
        worksheet.write(row+9 , 1, 'Taxes (Rp)', normal_left_bold)     
        worksheet.write(row+10 , 1, 'PPN 10%', normal_left_unborder)
        worksheet.write(row+10 , 8, sum_all_ppn, format_number_unborder)                            
        worksheet.write(row+11 , 1, 'Sales by SKU', normal_left_bold)
        for key, value in sku_values.iteritems():
            row += 1
            worksheet.write(row+11, 1, key, normal_left_unborder)
            worksheet.write(row+11, 8, value, format_number_unborder)            
            total_all_sales += value
        total_all_sales += sum_all_ppn
        worksheet.write(row+12 , 1, 'Total Sales (Rp)', normal_left_bold)                        
        worksheet.write(row+12 , 8, sum_total, format_number_bold_minbord)
        worksheet.write(row+13 , 1, 'Total Discount (Rp)', normal_left_bold)                        
        worksheet.write(row+13 , 8, sum_discount, format_number_bold_minbord)                                    
        workbook.close()

        out = base64.encodestring(bz.getvalue())
        self.write({'state_x':'get', 'data_x':out, 'name': filename})

        ir_model_data = self.env['ir.model.data']
        bz.close()
        form_res = ir_model_data.get_object_reference('pti_mds_sales_per_item', 'mds_sales_each_item_report_wizard_view')
        form_id = form_res and form_res[1] or False
        
        return {
            'name': ('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mds.sales.each.item.report.wizard',
            'res_id': self.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }




