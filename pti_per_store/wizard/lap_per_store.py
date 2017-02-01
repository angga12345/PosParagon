from openerp import models, fields, api
from cStringIO import StringIO
from datetime import datetime, timedelta
import xlsxwriter
import base64
import time
from jinja2.runtime import to_string
from gdata.contentforshopping.data import Domain
import pytz


class pos_config_cash_model(models.Model):
    _inherit = 'pos.config'
    
    cash_balance = fields.Float(related='last_session_closing_cash')
  
class RekapPenjProdukWBH(models.TransientModel):
    _name = "rekap.penj.prod.wbh.per.store"
    store = fields.Many2one('pos.config' , string="Store", domain=[('category_shop', '=','stand_alone'), ('stand_alone_categ', '=', 'wbh')])
    start_period = fields.Date(string="Start Period")
    end_period = fields.Date(string="End Period")
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    check_all=fields.Boolean('Check')
    
    def _get_data_product(self, end_period, start_period, store_name):
#         data_obj = [[]]
        self.env.cr.execute("""
        select pp.name_template, pol.price_unit, round(sum(pol.qty)/(select count(rel.product_template_id) 
                from pos_product_category_product_template_rel rel where rel.product_template_id = prel.product_template_id)) 
                as quantity, pol.discount, round(pol.price_unit*round(sum(pol.qty)/(select count(rel.product_template_id) 
                from pos_product_category_product_template_rel rel where rel.product_template_id = prel.product_template_id))*pol.discount/100) as total_disc,
                round(pol.price_unit*round(sum(pol.qty)/(select count(rel.product_template_id) 
                from pos_product_category_product_template_rel rel where rel.product_template_id = prel.product_template_id))) as total,
                round((pol.price_unit*round(sum(pol.qty)/(select count(rel.product_template_id) 
                from pos_product_category_product_template_rel rel where rel.product_template_id = prel.product_template_id))) * 0.1) as ppn
                from pos_order_line pol 
                join pos_order po on po.id = pol.order_id
                join pos_session ps on ps.id = po.session_id
                join pos_config pc on pc.id = ps.config_id
                join product_product pp on pol.product_id = pp.id,
                pos_product_category_product_template_rel prel,
                pos_product_category pcategory
                 where (pcategory.parent_id != (select id from pos_product_category where name = %s limit 1) or pcategory.parent_id is null)
                 AND po.date_order <= %s
                 AND po.date_order >= %s
                 AND (pp.voucher = 'false' or pp.voucher is null) 
                 AND pc.id = %s
                 AND prel.product_template_id = pp.product_tmpl_id
                 AND pcategory.id = prel.pos_product_category_id
                GROUP By pp.id, pol.qty, pol.price_unit, pol.discount, prel.product_template_id, price_subtotal_rel
                order by pp.name_template
                """, ('WBH', end_period+' 23:59:59', start_period+' 00:00:00', store_name))
        data_obj = self.env.cr.fetchall()
        return data_obj
        
    def _get_data_balance(self, end_period, start_period, store_name):
#         data_obj = [[]]
        self.env.cr.execute("""
            select sum(paccount.balance_start) as balance
                from pos_session psession join pos_config pconfig on psession.config_id = pconfig.id
                join account_bank_statement paccount on psession.id = paccount.pos_session_id
                join account_journal pjournal on pjournal.id = paccount.journal_id 
                where psession.start_at >= %s 
                and psession.start_at <= %s 
                and pjournal.type = 'cash'
                and pconfig.id = %s
                """, (end_period+' 23:59:59', start_period+' 00:00:00', store_name))
        data_obj = self.env.cr.fetchall()
        return data_obj
    
    def _get_data_max_rewards(self, end_period, start_period, store_name):
#         data_obj = [[]]
        self.env.cr.execute("""
            select po.max_reward_value as reward, lreward.name from pos_order po
                join pos_session ps on ps.id = po.session_id
                join pos_config pc on pc.id = ps.config_id
                join loyalty_reward lreward on lreward.id = po.loyalty_reward_id
                join loyalty_program lprogram on lprogram.id = lreward.loyalty_program_id
                where po.date_order <= %s
                AND po.date_order >= %s
                AND pc.id = %s
                AND po.is_max_reward = True
                    """, (end_period+' 23:59:59', start_period+' 00:00:00', store_name))
        data_obj = self.env.cr.fetchall()
        return data_obj
    
    def _get_data_special_price(self, end_period, start_period, store_name):
#         data_obj = [[]]
        self.env.cr.execute("""
            select sum(pol.price_subtotal_incl_rel / (select count(rel.product_template_id) 
                from pos_product_category_product_template_rel rel 
                where rel.product_template_id = prel.product_template_id)) - po.special_price as DiscountSpecialPrice,
                lreward.name
                from pos_order_line pol join pos_order po on po.id = pol.order_id
                join pos_session ps on ps.id = po.session_id
                join pos_config pc on pc.id = ps.config_id
                join product_product pp on pol.product_id = pp.id
                join loyalty_reward lreward on lreward.id = po.loyalty_reward_id
                join loyalty_program lprogram on lprogram.id = lreward.loyalty_program_id,
                pos_product_category_product_template_rel prel,
                pos_product_category pcategory
                where (pcategory.parent_id != (select id from pos_product_category where name = %s limit 1) or pcategory.parent_id is null)
                 AND po.date_order <= %s
                 AND po.date_order >= %s
                 AND pol.is_special_price = True
                 AND pc.id = %s
                 AND prel.product_template_id = pp.product_tmpl_id
                 AND pcategory.id = prel.pos_product_category_id
                group by po.id, lreward.name
                    """, ('WBH', end_period+' 23:59:59', start_period+' 00:00:00', store_name))
        data_obj = self.env.cr.fetchall()
        return data_obj
    
    def _get_data_voucher(self, start_period, end_period, store_name):
#         data_obj = [[]]
        self.env.cr.execute("""
                select pp.name_template as product, po_line.price_unit as price, sum(po_line.qty) as qty, 
                sum(po_line.price_subtotal_rel) as total
                        from pos_order_line po_line join pos_order po on po.id = po_line.order_id
                        join product_product pp on po_line.product_id = pp.id
                        join product_template pt on pt.id = pp.product_tmpl_id
                        join pos_session psession on po.session_id = psession.id
                        join pos_config pconfig on psession.config_id = pconfig.id
                        where po.date_order >= %s AND po.date_order <= %s
                        AND pconfig.category_shop = 'stand_alone'
                        AND AND pconfig.id = %s
                        AND pt.voucher = 'true' group by pp.name_template, po_line.qty, po_line.price_unit, po_line.price_subtotal_rel
                        order by pp.name_template
                        """, (start_period+' 00:00:00', end_period+' 23:59:59', store_name))
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

        filename = 'Rekapitulasi Penjualan Produk WBH Per Store '+self.store.name+'.xlsx'

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
        #################################################################################
        normal_border = workbook.add_format({'valign':'vcenter','align':'left'})
        normal_border.set_text_wrap()
        normal_border.set_font_name('Arial')
        normal_border.set_font_size('10')
        normal_border.set_border()
        
    
        worksheet = workbook.add_worksheet("report")
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 60)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 5)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        
        worksheet.merge_range('A1:J1', 'REKAPITULASI PENJUALAN PRODUK', normal_center_border)
        worksheet.merge_range('A2:C2','Nama Store : '+self.store.name, normal_left_bold)
        worksheet.write('B3','Start Period :', normal_left_unborder)
        worksheet.write('B4', sp.strftime('%d %b %Y'), normal_left_unborder)
        worksheet.write('D3', 'End Period :', normal_left_unborder)
        worksheet.write('D4', ep.strftime('%d %b %Y'),normal_left_unborder) 
        worksheet.write('F3', 'Print Date :', normal_left_unborder)
        worksheet.write('F4', utc_tz.strftime('%d %b %Y %H:%M'), normal_left_unborder) 
        
        worksheet.merge_range('A6:A7', 'No.', normal_bold_border)
        worksheet.merge_range('B6:B7', 'Product',normal_bold_border)
        worksheet.merge_range('C6:C7', 'Price', normal_bold_border)
        worksheet.merge_range('D6:D7', 'Qty',normal_bold_border)
        worksheet.merge_range('E6:F6', 'Discount', normal_bold_border)
        worksheet.write('E7','%', normal_bold_border)
        worksheet.write('F7','Rp', normal_bold_border)
        worksheet.merge_range('G6:G7', 'Total', normal_bold_border)
        worksheet.merge_range('H6:H7', 'Ppn', normal_bold_border)
        worksheet.freeze_panes(7,3)
                   
        row = 0
        number = 1
        inc = 0
        sum_total    = 0.0
        sum_ppn      = 0.0
        sum_discount = 0.0
        sum_cash = 0.0
        sum_voucher = 0.0
        sum_total_setor = 0.0
        store_name = self.store.id
        
        obj_pos = self._get_data_product(end_period, start_period, store_name)                      
        obj_pos_cash = self._get_data_balance(end_period, start_period, store_name)
        obj_pos_voucher = self._get_data_voucher(start_period, end_period, store_name)
        obj_pos_max_reward = self._get_data_max_rewards(end_period, start_period, store_name)
        obj_pos_special_price = self._get_data_special_price(end_period, start_period, store_name)
                   
        for cash in obj_pos_cash:
            if cash[0]:
                sum_cash += cash[0]
        sku_list = {}
        for pos in obj_pos:
            worksheet.write(row+7 , 0, number, normal_center)
            worksheet.write(row+7 , 1, pos[0], normal_left)                        
            
            worksheet.write(row+7 , 2, pos[1], format_number)
            worksheet.write(row+7 , 3, pos[2], normal_center)            
            if pos[3]==0:
                worksheet.write(row+7 , 4, '', normal_center)
                worksheet.write(row+7 , 5, '', format_number)        
            else:
                worksheet.write(row+7 , 4, pos[3], normal_center)
                worksheet.write(row+7 , 5, pos[4], format_number)                                    
            worksheet.write(row+7 , 6, pos[5], format_number)  
            worksheet.write(row+7 , 7, pos[6], format_number)
            
            sum_total    += pos[5]
            sum_ppn      += pos[6]
            sum_discount += pos[4]
                        
            number += 1
            row += 1
            
        for max_reward in obj_pos_max_reward:
            worksheet.write(row+7 , 0, number, normal_center)
            worksheet.write(row+7 , 1, 'Cashback ' + max_reward[1], normal_left)                        
            
            worksheet.write(row+7 , 2, max_reward[0], format_number)
            worksheet.write(row+7 , 3, '1', normal_center)            
            worksheet.write(row+7 , 4, '', normal_center)
            worksheet.write(row+7 , 5, '', format_number)                                    
            worksheet.write(row+7 , 6, -max_reward[0], format_number)  
            worksheet.write(row+7 , 7, '', format_number)
             
            sum_total    -= max_reward[0]
            sum_discount += max_reward[0]
                                   
            number += 1
            row += 1
        
        for special in obj_pos_special_price:
            worksheet.write(row+7 , 0, number, normal_center)
            worksheet.write(row+7 , 1, 'Discount Special Price ' + special[1] , normal_left)                        
            
            worksheet.write(row+7 , 2, special[0], format_number)
            worksheet.write(row+7 , 3, '1', normal_center)            
            worksheet.write(row+7 , 4, '', normal_center)
            worksheet.write(row+7 , 5, '', format_number)                                    
            worksheet.write(row+7 , 6, -special[0], format_number)  
            worksheet.write(row+7 , 7, '', format_number)
            
            sum_total    -= special[0]
            sum_discount += special[0]
                        
            number += 1
            row += 1                              
            
        if len(obj_pos)-1==inc or pos[0]!=obj_pos[inc+1][0]:
            worksheet.merge_range('A'+str(row+8)+':'+'F'+str(row+8), 'Total Penjualan(Rp)', normal_bold_border)
            worksheet.write(row+7 , 4, '', normal_center)
            worksheet.write(row+7 , 5, '', normal_center)
            worksheet.write(row+7 , 6, '', format_number_bold)        
            worksheet.write(row+7 , 7, '', format_number_bold)        
            worksheet.write(row+7 , 6, sum_total, format_number_bold)  
            worksheet.write(row+7 , 7, sum_ppn, format_number_bold)                
            row +=1
            number = 1 
        inc += 1
        
        for voucher in obj_pos_voucher:
            worksheet.write(row+7 , 1, voucher[0], normal_left)
            worksheet.write(row+7 , 2, voucher[1], format_number)
            worksheet.write(row+7 , 3, voucher[2], normal_center)
            worksheet.write(row+7 , 4, '', normal_center)
            worksheet.write(row+7 , 5, '', normal_center)
            worksheet.write(row+7 , 6, voucher[3], format_number_bold)
            worksheet.write(row+7 , 7, '', format_number_bold)
            row +=1
            sum_voucher += voucher[3]
            
        worksheet.write(row+7 , 0, '', normal_center)    
        worksheet.write(row+7 , 1, 'Modal Kembalian', normal_left)
        worksheet.write(row+7 , 2, '', normal_center)
        worksheet.write(row+7 , 3, '', normal_center)
        worksheet.write(row+7 , 4, '', normal_center)
        worksheet.write(row+7 , 5, '', normal_center)
        worksheet.write(row+7 , 6, sum_cash, format_number_bold)
        worksheet.write(row+7 , 7, '', format_number_bold)
        row += 8
        worksheet.merge_range('A'+str(row+1)+':'+'F'+str(row+1), 'Total Uang Disetor', normal_bold_border)
        sum_uang = sum_total + sum_voucher
        worksheet.write(row , 6, sum_uang, format_number_bold)
        worksheet.write(row , 7, sum_ppn, format_number_bold)


        worksheet.write(row+2 , 1, 'Taxes (Rp)', normal_left_bold)    
        worksheet.write(row+3 , 1, 'PPN 10%', normal_left_unborder)
        worksheet.write(row+3 , 6, sum_ppn, format_number_unborder)                            
 
        worksheet.write(row+4 , 1, 'Total Sales (Rp)', normal_left_bold)                        
        worksheet.write(row+4 , 6, sum_total, format_number_bold_minbord)                                    
         
        worksheet.write(row+5 , 1, 'Total Discount (Rp)', normal_left_bold)                        
        worksheet.write(row+5 , 6, sum_discount, format_number_bold_minbord)
                                             
        worksheet.write(row+6 , 1, 'Total Voucher (Rp)', normal_left_bold)                        
        worksheet.write(row+6 , 6, sum_voucher, format_number_bold_minbord)                                    
 
        worksheet.write(row+7 , 1, 'Total Uang Disetor (Rp)', normal_left_bold)                        
        worksheet.write(row+7 , 6, sum_uang, format_number_bold_minbord)                                            
        workbook.close()

        out = base64.encodestring(bz.getvalue())
        self.write({'state_x':'get', 'data_x':out, 'name': filename})

        ir_model_data = self.env['ir.model.data']
        bz.close()
        form_res = ir_model_data.get_object_reference('pti_per_store', 'rekap_penj_prod_wbh_per_store')
        form_id = form_res and form_res[1] or False
        
        return {
            'name': ('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'rekap.penj.prod.wbh.per.store',
            'res_id': self.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }


