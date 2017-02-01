from openerp import models, fields, api
from cStringIO import StringIO
from datetime import datetime, timedelta
import xlsxwriter
import base64
import time
from jinja2.runtime import to_string

    
class LaporanPenjPromoDiscReportIdepStoreWizard(models.TransientModel):
    _name = "lap.penj.promo.disc.idep.store.wizard"

    start_period = fields.Date(string="Start Period")
    end_period = fields.Date(string="End Period")
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    check_all=fields.Boolean('Check')
    store_name = fields.Many2one("pos.config", string="Store", 
                                 domain=[('category_shop', '=','stand_alone'),
                                         ('stand_alone_categ','=','independent')])

    @api.multi
    def generate_excel_lap_penj_promo_disc(self):
        for this in self:
            start_period = this.start_period
            end_period = this.end_period
            today = datetime.now()
            start_period = datetime.strptime(start_period, '%Y-%m-%d')
            end_period = datetime.strptime(end_period, '%Y-%m-%d')
            store = self.store_name
            bz = StringIO()
            workbook = xlsxwriter.Workbook(bz)

            filename = 'Laporan Penj Promo Per Discount' + store.name + '.xls'
            #################################################################################
            center_title = workbook.add_format({'bold': 1, 'valign': 'vcenter', 'align': 'center'})
            center_title.set_text_wrap()
            center_title.set_font_name('Arial')
            center_title.set_font_size('12')
            #################################################################################
            normal_left = workbook.add_format({'valign': 'bottom', 'align': 'left'})
            normal_left.set_font_name('Arial')
            normal_left.set_font_size('10')
            #################################################################################
            normal_left_bold = workbook.add_format({'bold': 1, 'valign': 'bottom', 'align': 'left'})
            normal_left_bold.set_font_name('Arial')
            normal_left_bold.set_font_size('10')
            #################################################################################
            normal_left_border = workbook.add_format({'valign':'bottom','align':'left'})
            normal_left_border.set_text_wrap()
            normal_left_border.set_font_name('Arial')
            normal_left_border.set_font_size('10')
            normal_left_border.set_border()
            #################################################################################
            normal_right_border = workbook.add_format({'valign':'bottom','align':'right'})
            normal_right_border.set_text_wrap()
            normal_right_border.set_font_name('Arial')
            normal_right_border.set_font_size('10')
            normal_right_border.set_border()
            #################################################################################
            normal_center_border = workbook.add_format({'align':'center'})
            normal_center_border.set_text_wrap()
            normal_center_border.set_font_name('Arial')
            normal_center_border.set_font_size('10')
            normal_center_border.set_border()
            normal_center_border.set_align('center')
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
            normal_border = workbook.add_format({'valign':'vcenter','align':'left'})
            normal_border.set_text_wrap()
            normal_border.set_font_name('Arial')
            normal_border.set_font_size('10')
            normal_border.set_border()
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
            format_number_bold_unborder = workbook.add_format({'bold': 1,'valign':'vcenter','align':'right'})
            format_number_bold_unborder.set_num_format('#,##0.00')
            format_number_bold_unborder.set_font_name('Arial')
            format_number_bold_unborder.set_font_size('10')

            worksheet = workbook.add_worksheet("Lap Penj Promo Disc")
            worksheet.set_column('A:A', 25)
            worksheet.set_column('B:B', 55)
            worksheet.set_column('C:C', 10)
            worksheet.set_column('D:D', 6)
            worksheet.set_column('E:E', 4)
            worksheet.set_column('F:F', 14)
            worksheet.set_column('G:G', 16)
            worksheet.set_column('H:H', 14)

            worksheet.merge_range('A1:H1', 'Laporan Penjualan Promo Discount', center_title)
            worksheet.write('A3', 'Store Name :', normal_left_bold)
            worksheet.write('A4', store.name, normal_left)
            worksheet.write('A5', 'Start Period :', normal_left_bold)
            worksheet.write('A6', start_period.strftime('%d %b %Y'), normal_left)
            worksheet.write('B5', 'End Period :', normal_left_bold)
            worksheet.write('B6', end_period.strftime('%d %b %Y'), normal_left)
            worksheet.write('D5', 'Print Date :', normal_left_bold)
            worksheet.write('D6', today.strftime('%d %b %Y %H:%M'), normal_left)

            worksheet.merge_range('A8:A9', 'Period Promo', normal_bold_border)
            worksheet.merge_range('B8:B9', 'Product', normal_bold_border)
            worksheet.merge_range('C8:C9', 'Price', normal_bold_border)
            worksheet.merge_range('D8:D9', 'Qty', normal_bold_border)
            worksheet.merge_range('E8:F8', 'Disc.', normal_bold_border)
            worksheet.write('E9', '%', normal_bold_border)
            worksheet.write('F9', 'Rp', normal_bold_border)
            worksheet.merge_range('G8:G9', 'Total', normal_bold_border)
            worksheet.merge_range('H8:H9', 'Ppn', normal_bold_border)
            worksheet.freeze_panes(9, 2)

            self.env.cr.execute(
                """
                select distinct to_char(lprogram.start_date,'DD Mon YYYY'), to_char(lprogram.end_date,'DD Mon YYYY'),
                lreward.name,
                sum (pol.price_subtotal_incl_rel) - po.special_price, 
                (select distinct count(id) from pos_order where loyalty_reward_id = lreward.id),
                lreward.id
                from pos_order_line pol join pos_order po on po.id = pol.order_id
                join pos_session ps on ps.id = po.session_id
                join pos_config pc on pc.id = ps.config_id
                join loyalty_reward lreward on lreward.id = po.loyalty_reward_id
                join loyalty_program lprogram on lprogram.id = lreward.loyalty_program_id
                where po.date_order >= %s
                 AND po.date_order <= %s
                 AND pol.is_special_price = True
                 AND pc.id = %s
                group by po.id, lreward.id, lprogram.start_date, lprogram.end_date
                """
                ,(this.start_period+' 00:00:00', this.end_period+' 23:59:59', store.id))
            special_pricess = self.env.cr.fetchall()

            self.env.cr.execute(
                """
                select distinct pp.name_template, sum(pol.qty), pol.price_unit, lreward.id
                from pos_order_line pol join pos_order po on po.id = pol.order_id
                join pos_session ps on ps.id = po.session_id
                join pos_config pc on pc.id = ps.config_id
                join loyalty_reward lreward on lreward.id = po.loyalty_reward_id
                join loyalty_program lprogram on lprogram.id = lreward.loyalty_program_id
                join product_product pp on pp.id = pol.product_id
                where po.date_order >= %s
                 AND po.date_order <= %s
                 AND pol.is_special_price = True
                 AND pc.id = %s
                group by pp.name_template, lreward.id, pol.price_unit
                """
                , (this.start_period + ' 00:00:00', this.end_period + ' 23:59:59', store.id))
            product_special_prices = self.env.cr.fetchall()

            self.env.cr.execute(
                """
                select to_char(lprogram.start_date,'DD Mon YYYY'), to_char(lprogram.end_date,'DD Mon YYYY'),
                lreward.name,
                sum(porder.max_reward_value) as max_reward_value, 
                count(porder.id),
                0,
                0,
                -sum(porder.max_reward_value) as max_reward_value,
                0,
                lreward.id
                from pos_order porder 
                    join loyalty_reward lreward on lreward.id = porder.loyalty_reward_id
                    join loyalty_program lprogram on lprogram.id = lreward.loyalty_program_id
                    join pos_session psession on psession.id = porder.session_id
                    join pos_config pconfig on pconfig.id = psession.config_id
                where porder.date_order >= %s
                    AND porder.date_order <= %s
                    and porder.max_reward_value is not null
                    AND pconfig.id = %s
                group by lprogram.start_date, lprogram.end_date, lreward.discount_pti,lreward.name, lreward.id
                order by lprogram.start_date
                """
                , (this.start_period+' 00:00:00', this.end_period+' 23:59:59', store.id))
            max_pricess = self.env.cr.fetchall()

            self.env.cr.execute(
                """
                select distinct pp.name_template, sum(pol.qty), pol.price_unit, lreward.id
                from pos_order_line pol join pos_order po on po.id = pol.order_id
                join pos_session ps on ps.id = po.session_id
                join pos_config pc on pc.id = ps.config_id
                join loyalty_reward lreward on lreward.id = po.loyalty_reward_id
                join loyalty_program lprogram on lprogram.id = lreward.loyalty_program_id
                join product_product pp on pp.id = pol.product_id
                where po.date_order >= '2017-01-01 00:00:00'
                 AND po.date_order <= '2017-01-31 00:00:00'
                 AND po.is_max_reward = True
                 AND pc.id = 16
                group by pp.name_template, lreward.id, pol.price_unit
                """
                , (this.start_period + ' 00:00:00', this.end_period + ' 23:59:59', store.id))
            product_max_prices = self.env.cr.fetchall()

            self.env.cr.execute("""
                select to_char(lprogram.start_date,'DD Mon YYYY'), to_char(lprogram.end_date,'DD Mon YYYY'),
                pproduct.name_template, pline.price_unit, sum(pline.qty), pline.discount,
                (pline.price_unit * sum(pline.qty)) * (pline.discount / 100),
                (pline.price_unit * sum(pline.qty)) - ((pline.price_unit * sum(pline.qty)) * (pline.discount / 100)),
                ((pline.price_unit * sum(pline.qty)) - ((pline.price_unit * sum(pline.qty)) * (pline.discount / 100))) * 0.1,
                ptemplate.type
                from pos_order_line pline join pos_order porder on porder.id = pline.order_id 
                join loyalty_reward lreward on lreward.id = porder.loyalty_reward_id
                join loyalty_program lprogram on lprogram.id = lreward.loyalty_program_id
                join product_product pproduct on pproduct.id = pline.product_id
                join product_template ptemplate on pproduct.product_tmpl_id = ptemplate.id
                join pos_session psession on psession.id = porder.session_id
                join pos_config pconfig on pconfig.id = psession.config_id
                where porder.date_order >= %s
                         AND porder.date_order <= %s and pline.discount > 0
                         AND pconfig.id = %s
                         group by pline.discount, pline.price_unit, lprogram.start_date, lprogram.end_date, pproduct.name_template, ptemplate.type
                order by lprogram.start_date
                """, (this.start_period+' 00:00:00', this.end_period+' 23:59:59', store.id))

            obj_pos = self.env.cr.fetchall()
            row = 1
            inc = 0
            sum_total = 0.0
            sum_ppn = 0.0
            sum_disc = 0.0
            product_qty = 0
            treatment_qty = 0
            
            for pos in obj_pos:
                worksheet.write(row+8, 0, pos[0] + ' - ' + pos[1], normal_left_border)
                worksheet.write(row+8, 1, pos[2], normal_left_border)
                worksheet.write(row+8, 2, pos[3], format_number)
                worksheet.write(row+8, 3, pos[4], normal_center_border)
                worksheet.write(row+8, 4, pos[5], normal_center_border)
                worksheet.write(row+8, 5, pos[6], format_number)
                worksheet.write(row+8, 6, pos[7], format_number)
                worksheet.write(row+8, 7, pos[8], format_number)
                sum_disc += pos[6]
                sum_total += pos[7]
                sum_ppn += pos[8]
                row += 1

                if pos[9] == 'product':
                    product_qty += pos[4]
                elif pos[9] == 'service':
                    treatment_qty += pos[4]
            for max_price in max_pricess:
                for max_price_product in product_max_prices:
                    if max_price_product[3] == max_price[9]:
                        worksheet.write(row+8, 0, max_price[0] + ' - ' + max_price[1], normal_left_border)
                        worksheet.write(row+8, 1, max_price_product[0], normal_left_border)
                        worksheet.write(row+8, 2, max_price_product[2], format_number)
                        worksheet.write(row+8, 3, max_price_product[1], normal_center_border)
                        worksheet.write(row+8, 4, 0, normal_center_border)
                        worksheet.write(row+8, 5, 0, format_number)
                        worksheet.write(row+8, 6, max_price_product[2] * max_price_product[1], format_number)
                        worksheet.write(row+8, 7, (max_price_product[2] * max_price_product[1]) * 0.1, format_number)
                        row += 1
                worksheet.write(row+8, 0, max_price[0] + ' - ' + max_price[1], normal_left_border)
                worksheet.write(row+8, 1, 'Cashback ' + max_price[2], normal_left_border)
                worksheet.write(row+8, 2, max_price[3], format_number)
                worksheet.write(row+8, 3, max_price[4], normal_center_border)
                worksheet.write(row+8, 4, max_price[5], normal_center_border)
                worksheet.write(row+8, 5, max_price[6], format_number)
                worksheet.write(row+8, 6, max_price[7], format_number)
                worksheet.write(row+8, 7, max_price[8], format_number)
                sum_disc += max_price[6]
                sum_total += max_price[7]
                sum_ppn += max_price[8]
                row += 1

            for special_prices in special_pricess:
                for product in product_special_prices:
                    if product[3] == special_prices[5]:
                        worksheet.write(row+8, 0, special_prices[0] + ' - ' + special_prices[1], normal_left_border)
                        worksheet.write(row+8, 1, product[0], normal_left_border)
                        worksheet.write(row+8, 2, product[2], format_number)
                        worksheet.write(row+8, 3, product[1], normal_center_border)
                        worksheet.write(row+8, 4, 0, normal_center_border)
                        worksheet.write(row+8, 5, 0, format_number)
                        worksheet.write(row+8, 6, product[2] * product[1], format_number)
                        worksheet.write(row+8, 7, (product[2] * product[1]) * 0.1, format_number)
                        row += 1
                worksheet.write(row+8, 0, special_prices[0] + ' - ' + special_prices[1], normal_left_border)
                worksheet.write(row+8, 1, 'Discount ' + special_prices[2], normal_left_border)
                worksheet.write(row+8, 2, special_prices[3], format_number)
                worksheet.write(row+8, 3, special_prices[4], normal_center_border)
                worksheet.write(row+8, 4, 0, normal_center_border)
                worksheet.write(row+8, 5, 0, format_number)
                worksheet.write(row+8, 6, -special_prices[3], format_number)
                worksheet.write(row+8, 7, 0, format_number)
                sum_total += special_prices[3]
                row += 1

            worksheet.write(row+8, 0, '', normal_left_border)
            worksheet.write(row+8, 1, '', normal_left_border)
            worksheet.write(row+8, 2, '', normal_left_border)
            worksheet.write(row+8, 3, '', normal_left_border)
            worksheet.write(row+8, 4, '', normal_left_border)
            worksheet.write(row+8, 5, sum_disc, format_number_bold)
            worksheet.write(row+8, 6, sum_total, format_number_bold)
            worksheet.write(row+8, 7, sum_ppn, format_number_bold)
            
            row = row+1

            worksheet.write(row+9, 0, 'Taxes (Rp)', normal_left_bold)
            worksheet.write(row+10, 0, 'PPN 10%', normal_left)
            worksheet.write(row+10, 6, sum_ppn, format_number_unborder)
            worksheet.write(row+11, 0, 'Total Sales (Rp)', normal_left_bold)
            worksheet.write(row+11, 6, sum_total, format_number_bold_unborder)
            worksheet.write(row+12, 0, 'Qty of Product (Pcs)', normal_left_bold)
            worksheet.write(row+12, 6, product_qty, format_number_unborder)
            worksheet.write(row+13, 0, 'Qty of Treatment', normal_left_bold)
            worksheet.write(row+13, 6, treatment_qty, format_number_unborder)
            worksheet.write(row+14, 0, 'Total Discount (Rp)', normal_left_bold)
            worksheet.write(row+14, 6, sum_disc, format_number_bold_unborder)
            workbook.close()

            out = base64.encodestring(bz.getvalue())
            this.write({'state_x':'get', 'data_x':out, 'name': filename})

            ir_model_data = self.env['ir.model.data']
            bz.close()
            form_res = ir_model_data.get_object_reference('pti_pos_independent_store_report', 'independent_store_report_lap_penj_promo_disc_wizard_view')
            form_id = form_res and form_res[1] or False                                             
            
            return {
                'name': ('Download XLS'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'lap.penj.promo.disc.idep.store.wizard',
                'res_id': this.id,
                'view_id': False,
                'views': [(form_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current'
            }

