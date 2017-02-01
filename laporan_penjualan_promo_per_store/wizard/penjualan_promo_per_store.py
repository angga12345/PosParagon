from openerp import models, fields, api
from cStringIO import StringIO
from datetime import datetime, timedelta
import xlsxwriter
import base64
import time
from jinja2.runtime import to_string

    
class LaporanPromoPerStoreReportWizard(models.TransientModel):
    _name = "laporan.promo.per.store.report.wizard"

    start_period = fields.Date(string="Start Period")
    end_period = fields.Date(string="End Period")
    store_name = fields.Many2one("pos.config", string="Store", domain=[('category_shop', '=','shop_in_shop_mds')])
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    check_all=fields.Boolean('Check')

    @api.multi
    def generate_excel(self):
        form_bc_obj = self.env['pos.order']
        for this in self:
            start_period = this.start_period
            end_period = this.end_period
            today = datetime.now()
            sp=datetime.strptime(start_period, '%Y-%m-%d')
            ep=datetime.strptime(end_period, '%Y-%m-%d')
            sn = self.store_name.name
            sn_id = self.store_name.id
            
            bz = StringIO()
            workbook = xlsxwriter.Workbook(bz)
            fn = 'Laporan Penjualan Promo '+sn+'.xls'

            filename = fn


            #### STYLE
            #################################################################################
            center_title = workbook.add_format({'bold': 1,'valign':'vcenter','align':'center'})
            center_title.set_text_wrap()
            center_title.set_font_name('Arial')
            center_title.set_font_size('12')
            #################################################################################
            normal_left = workbook.add_format({'valign':'bottom','align':'left'})
            normal_left.set_font_name('Arial')
            normal_left.set_font_size('10')
            #################################################################################
            normal_left_bold = workbook.add_format({'bold' :1, 'valign':'bottom','align':'left'})
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

            
            worksheet = workbook.add_worksheet("Lap Penj Promo per Store")
            worksheet.set_column('A:A', 25)
            worksheet.set_column('B:B', 55)
            worksheet.set_column('C:C', 12)
            worksheet.set_column('D:D', 10)
            worksheet.set_column('E:E', 6)
            worksheet.set_column('F:F', 4)
            worksheet.set_column('G:G', 14)
            worksheet.set_column('H:H', 16)
            worksheet.set_column('I:I', 14)
            
            worksheet.write('A1', 'Laporan Penjualan Promo '+sn, normal_left_bold)
            worksheet.write('B3','Start Period :',normal_left_bold)
            worksheet.write('B4', sp.strftime('%d %b %Y'),normal_left)
            worksheet.write('C3', 'End Period :',normal_left_bold)
            worksheet.write('C4', ep.strftime('%d %b %Y'),normal_left) 
            worksheet.write('F3', 'Print Date :',normal_left_bold)
            worksheet.write('F4', today.strftime('%d %b %Y'),normal_left) 
            
            worksheet.merge_range('A5:A6', 'Period Promo', normal_bold_border)
            worksheet.merge_range('B5:B6', 'Product', normal_bold_border)
            worksheet.merge_range('C5:C6', 'SKU', normal_bold_border)
            worksheet.merge_range('D5:D6', 'Price', normal_bold_border)
            worksheet.merge_range('E5:E6', 'Qty', normal_bold_border)
            worksheet.merge_range('F5:G5', 'Disc.', normal_bold_border)
            worksheet.write('F6', '%', normal_bold_border)
            worksheet.write('G6', 'Rp', normal_bold_border)
            worksheet.merge_range('H5:H6', 'Total', normal_bold_border)
            worksheet.merge_range('I5:I6', 'Ppn', normal_bold_border)
            worksheet.freeze_panes(6,0)

            self.env.cr.execute(
                """
                select distinct to_char(lprogram.start_date,'DD Mon YYYY'), to_char(lprogram.end_date,'DD Mon YYYY'),
                lreward.name,
                po.shop_identifier_period,
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
                group by po.id, lreward.id, lprogram.start_date, lprogram.end_date, po.shop_identifier_period
                """
                , (this.start_period + ' 00:00:00', this.end_period + ' 23:59:59', sn_id))
            special_pricess = self.env.cr.fetchall()

            self.env.cr.execute(
                """
                select distinct pp.name_template, po.shop_identifier_period, sum(pol.qty), pol.price_unit, lreward.id
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
                group by pp.name_template, lreward.id, pol.price_unit, po.shop_identifier_period
                """
                , (this.start_period + ' 00:00:00', this.end_period + ' 23:59:59', sn_id))
            product_special_prices = self.env.cr.fetchall()

            self.env.cr.execute(
                """
                select to_char(lprogram.start_date,'DD Mon YYYY'), to_char(lprogram.end_date,'DD Mon YYYY'),
                lreward.name, porder.shop_identifier_period,
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
                group by lprogram.start_date, lprogram.end_date, lreward.discount_pti,lreward.name, lreward.id, porder.shop_identifier_period
                order by lprogram.start_date
                """
                , (this.start_period + ' 00:00:00', this.end_period + ' 23:59:59', sn_id))
            max_pricess = self.env.cr.fetchall()

            self.env.cr.execute(
                """
                select distinct pp.name_template, po.shop_identifier_period, sum(pol.qty), pol.price_unit, lreward.id
                from pos_order_line pol join pos_order po on po.id = pol.order_id
                join pos_session ps on ps.id = po.session_id
                join pos_config pc on pc.id = ps.config_id
                join loyalty_reward lreward on lreward.id = po.loyalty_reward_id
                join loyalty_program lprogram on lprogram.id = lreward.loyalty_program_id
                join product_product pp on pp.id = pol.product_id
                where po.date_order >= %s
                 AND po.date_order <= %s
                 AND po.is_max_reward = True
                 AND pc.id = %s
                group by pp.name_template, lreward.id, pol.price_unit, po.shop_identifier_period
                """
                , (this.start_period + ' 00:00:00', this.end_period + ' 23:59:59', sn_id))
            product_max_prices = self.env.cr.fetchall()

            self.env.cr.execute("""
                            select to_char(lprogram.start_date,'DD Mon YYYY'), to_char(lprogram.end_date,'DD Mon YYYY'),
                            pproduct.name_template,
                            porder.shop_identifier_period,
                            pline.price_unit, sum(pline.qty), pline.discount,
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
                                     group by pline.discount, pline.price_unit, lprogram.start_date, lprogram.end_date, pproduct.name_template, ptemplate.type, porder.shop_identifier_period
                            order by lprogram.start_date
                            """, (this.start_period + ' 00:00:00', this.end_period + ' 23:59:59', sn_id))

            obj_pos = self.env.cr.fetchall()

            # self.env.cr.execute("""
            #     select to_char(lprogram.start_date,'DD Mon YYYY')|| ' - ' ||to_char(lprogram.end_date, 'DD Mon YYYY') as promo_date,
            #         pproduct.name_template as product,
            #             pconfig.shop_identifier_period as sku_period,
            #             round(pline.price_unit,2) as Price,
            #             sum(pline.qty) as Qty,
            #             pline.discount as disc,
            #             round((pline.price_unit * sum(pline.qty)) * (pline.discount / 100),2) as Rp,
            #             round((pline.price_unit * sum(pline.qty)) - ((pline.price_unit * sum(pline.qty)) * (pline.discount / 100)),2) as Total,
            #             round(((pline.price_unit * sum(pline.qty)) - ((pline.price_unit * sum(pline.qty)) * (pline.discount / 100))) * 0.1,2) as Ppn
            #     from pos_order_line pline
            #     join pos_order porder on porder.id = pline.order_id
            #     join loyalty_reward lreward on lreward.id = porder.loyalty_reward_id
            #     join loyalty_program lprogram on lprogram.id = lreward.loyalty_program_id
            #     join product_product pproduct on pproduct.id = pline.product_id
            #     join product_template ptemplate on pproduct.product_tmpl_id = ptemplate.id
            #     join pos_session psession on psession.id = porder.session_id
            #     join pos_config pconfig on pconfig.id = psession.config_id
            #     where pline.discount > 0 AND pconfig.shop_identifier_origin != '' AND pconfig.id = %s
            #     AND porder.date_order >= %s AND porder.date_order <= %s
            #     group by product, sku_origin, Price, Qty, lprogram.start_date, lprogram.end_date, disc, pline.price_unit
            #     union all
            #     select  to_char(ppricelistitem.date_start,'DD Mon YYYY')|| ' - ' ||to_char(ppricelistitem.date_end, 'DD Mon YYYY') as promo_date,
            #         pproduct.name_template as product,
            #             pconfig.shop_identifier_period as sku_period,
            #             round(pline.price_unit,2) as Price,
            #             sum(pline.qty) as Qty,
            #             pline.discount as disc,
            #             round((pline.price_unit * sum(pline.qty)) * (pline.discount / 100),2) as Rp,
            #             round((pline.price_unit * sum(pline.qty) - ((pline.price_unit * sum(pline.qty)) * (pline.discount / 100))),2) as Total,
            #             round((pline.price_unit * sum(pline.qty) - ((pline.price_unit * sum(pline.qty)) * (pline.discount / 100))) * 0.1,2) as Ppn
            #     from    pos_order as porder
            #     join    pos_order_line as pline on porder.id = pline.order_id
            #     join    product_pricelist as ppricelist on porder.pricelist_id = ppricelist.id
            #     join    product_pricelist_item as ppricelistitem on ppricelist.id = ppricelistitem.pricelist_id
            #     join    product_template as ptemplate on ppricelistitem.product_tmpl_id = ptemplate.id
            #     join    product_product as pproduct on pproduct.id = pline.product_id
            #     join    pos_session as psession on porder.session_id = psession.id
            #     join    pos_config as pconfig on psession.config_id = pconfig.id
            #     where pline.discount > 0 AND pconfig.shop_identifier_origin != '' AND pconfig.id = %s
            #     AND porder.date_order >= %s AND porder.date_order <= %s
            #     group by product, sku_origin, Price, Qty, ppricelistitem.date_start, ppricelistitem.date_end, disc, pline.price_unit
            #     union all
            #     select to_char(lprogram.start_date,'DD Mon YYYY')|| ' - ' ||to_char(lprogram.end_date, 'DD Mon YYYY') as promo_date,
            #         pproduct.name_template || ''|| lreward.name as product,
            #             pconfig.shop_identifier_period as sku_period,
            #             round(pline.price_unit,2) as Price,
            #             sum(lreward.max_reward_value) as Qty,
            #             pline.discount as disc,
            #             round(0,2) as Rp,
            #             (pline.price_unit*sum(pline.qty)-((pline.price_unit*sum(pline.qty))*(pline.discount/100)))-lreward.special_price  as Total,
            #             round(0,2) as Ppn
            #     from pos_order_line pline
            #     join pos_order porder on porder.id = pline.order_id
            #     join loyalty_reward lreward on lreward.id = porder.loyalty_reward_id
            #     join loyalty_program lprogram on lprogram.id = lreward.loyalty_program_id
            #     join product_product pproduct on pproduct.id = pline.product_id
            #     join product_template ptemplate on pproduct.product_tmpl_id = ptemplate.id
            #     join pos_session psession on psession.id = porder.session_id
            #     join pos_config pconfig on pconfig.id = psession.config_id
            #     where pline.discount > 0 AND pconfig.shop_identifier_origin != '' AND pconfig.id = %s
            #     AND porder.date_order >= %s AND porder.date_order <= %s
            #     group by product, sku_origin, Price, Qty, lprogram.start_date, lprogram.end_date, disc, pline.price_unit, lreward.special_price
            #     order by promo_date asc
            #     """, (sn_id,sn_id,sn_id,))
            #
            #
            # obj_pos = self.env.cr.fetchall()

            row=1
            number=1
            inc = 0
            sum_total = 0.0
            sum_ppn = 0.0
            sum_disc = 0.0
            sum_qt = 0.0
            total_all_sales = 0.0
            sku_list = {}

            for pos in obj_pos:
                worksheet.write(row+5, 0, pos[0] + ' - ' + pos[1], normal_left_border)
                worksheet.write(row+5, 1, pos[2], normal_left_border)
                sku = pos[3]
                if len(sku) > 8:
                    sku = sku[4:][:-1]  
                worksheet.write(row+5, 2, sku, normal_center_border)
                worksheet.write(row+5, 3, pos[4], format_number)
                worksheet.write(row+5, 4, pos[5], normal_center_border)
                worksheet.write(row+5, 5, pos[6], normal_center_border)
                worksheet.write(row+5, 6, pos[7], format_number)
                worksheet.write(row+5, 7, pos[8], format_number)
                worksheet.write(row+5, 8, pos[9], format_number)
                
                sku_list.update({ inc : [sku,pos[8]]})
                sum_qt += pos[5]
                sum_disc += pos[7]
                sum_total += pos[8]
                sum_ppn += pos[9]
                number += 1
                row +=1
                #
                # if len(obj_pos)-1==inc:
                #     worksheet.write(row+5 , 0, '', normal_left_border)
                #     worksheet.write(row+5 , 1, '', normal_left_border)
                #     worksheet.write(row+5 , 2, '', normal_left_border)
                #     worksheet.write(row+5 , 3, '', normal_left_border)
                #     worksheet.write(row+5 , 4, '', normal_left_border)
                #     worksheet.write(row+5 , 5, '', normal_left_border)
                #     worksheet.write(row+5 , 6, sum_disc, format_number_bold)
                #     worksheet.write(row+5 , 7, sum_total, format_number_bold)
                #     worksheet.write(row+5 , 8, sum_ppn, format_number_bold)
                #
                #     number = 1
                #     row = row+1
                inc += 1

            max_reward_id = 0
            for max_price in max_pricess:
                if max_reward_id != max_price[10]:
                    for max_price_product in product_max_prices:
                        if max_price_product[4] == max_price[10]:
                            max_reward_id = max_price[10]
                            worksheet.write(row+5, 0, max_price[0] + ' - ' + max_price[1], normal_left_border) #period promo
                            worksheet.write(row+5, 1, max_price_product[0], normal_left_border) # product
                            sku = max_price_product[1]
                            if len(sku) > 8:
                                sku = sku[4:][:-1]
                            worksheet.write(row+5, 2, sku, normal_center_border) # SKU
                            worksheet.write(row+5, 3, max_price_product[3], format_number) # price
                            worksheet.write(row+5, 4, max_price_product[2], normal_center_border) # qty
                            worksheet.write(row+5, 5, 0, normal_center_border) # disc %
                            worksheet.write(row+5, 6, 0, format_number)
                            worksheet.write(row+5, 7, max_price_product[3] * max_price_product[2], format_number) # disc rp
                            worksheet.write(row+5, 8, (max_price_product[3] * max_price_product[2]) * 0.1, format_number) # total
                            sku_list.update({inc: [sku, max_price_product[3] * max_price_product[2]]})
                            sum_qt += max_price_product[2]
                            sum_total += (max_price_product[3] * max_price_product[2])
                            sum_ppn += ((max_price_product[3] * max_price_product[2]) * 0.1)
                            row += 1
                            inc += 1
                sku = max_price[3]
                if len(sku) > 8:
                    sku = sku[4:][:-1]
                worksheet.write(row+5, 0, max_price[0] + ' - ' + max_price[1], normal_left_border) #period promo
                worksheet.write(row+5, 1, 'Cashback ' + max_price[2], normal_left_border) #product
                worksheet.write(row+5, 2, sku, normal_center_border) # SKU
                worksheet.write(row+5, 3, max_price[4], format_number) # price
                worksheet.write(row+5, 4, max_price[5], normal_center_border) # qty
                worksheet.write(row+5, 5, max_price[6], normal_center_border) # disc %
                worksheet.write(row+5, 6, max_price[7], format_number)# disc rp
                worksheet.write(row+5, 7, max_price[8], format_number)# total
                worksheet.write(row+5, 8, max_price[9], format_number)# total ppn
                sum_total += max_price[8]
                sku_list.update({inc: [sku, max_price[8]]})
                row += 1
                inc += 1

            special_price_id = 0
            for special_price in special_pricess:
                if special_price_id != special_price[6]:
                    for special_price_product in product_special_prices:
                        if special_price_product[4] == special_price[6]:
                            special_price_id = special_price[6]
                            worksheet.write(row+5, 0, special_price[0] + ' - ' + special_price[1], normal_left_border) #period promo
                            worksheet.write(row+5, 1, special_price_product[0], normal_left_border) # product
                            sku = special_price_product[1]
                            if len(sku) > 8:
                                sku = sku[4:][:-1]
                            worksheet.write(row+5, 2, sku, normal_center_border) # SKU
                            worksheet.write(row+5, 3, special_price_product[3], format_number) # price
                            worksheet.write(row+5, 4, special_price_product[2], normal_center_border) # qty
                            worksheet.write(row+5, 5, 0, normal_center_border) # disc %
                            worksheet.write(row+5, 6, 0, format_number) #disc rp
                            worksheet.write(row+5, 7, special_price_product[2] * special_price_product[3], format_number) # disc rp
                            worksheet.write(row+5, 8, (special_price_product[2] * special_price_product[3]) * 0.1, format_number) # total
                            sku_list.update({inc: [sku, special_price_product[2] * special_price_product[3]]})
                            sum_qt += special_price_product[2]
                            sum_total += (special_price_product[3] * special_price_product[2])
                            sum_ppn += ((special_price_product[3] * special_price_product[2]) * 0.1)
                            row += 1
                            inc += 1
                worksheet.write(row+5, 0, special_price[0] + ' - ' + special_price[1], normal_left_border) #period promo
                worksheet.write(row+5, 1, 'Discount ' + special_price[2], normal_left_border) #product
                sku = special_price[3]
                if len(sku) > 8:
                    sku = sku[4:][:-1]
                worksheet.write(row+5, 2, sku, normal_center_border) # SKU
                worksheet.write(row+5, 3, special_price[4], format_number) # price
                worksheet.write(row+5, 4, special_price[5], normal_center_border) # qty
                worksheet.write(row+5, 5, 0, normal_center_border) # disc %
                worksheet.write(row+5, 6, 0, format_number)# disc rp
                worksheet.write(row+5, 7, -special_price[4], format_number)# total
                worksheet.write(row+5, 8, 0, format_number)# total ppn
                sum_total += (special_price[4] * -1)
                sku_list.update({inc: [sku, (special_price[4] * -1)]})
                row += 1
                inc += 1

            worksheet.write(row+5 , 0, '', normal_left_border)
            worksheet.write(row+5 , 1, '', normal_left_border)
            worksheet.write(row+5 , 2, '', normal_left_border)
            worksheet.write(row+5 , 3, '', normal_left_border)
            worksheet.write(row+5 , 4, '', normal_left_border)
            worksheet.write(row+5 , 5, '', normal_left_border)
            worksheet.write(row+5 , 6, sum_disc, format_number_bold)
            worksheet.write(row+5 , 7, sum_total, format_number_bold)
            worksheet.write(row+5 , 8, sum_ppn, format_number_bold)
            row = row+1

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
    
            
            worksheet.write(row+7 , 1, 'Taxes (Rp)', normal_left_bold)     
            worksheet.write(row+8 , 1, 'PPN 10%', normal_left)
            worksheet.write(row+8 , 7, sum_ppn, format_number_unborder)                            
            worksheet.write(row+9 , 1, 'Sales by SKU', normal_left_bold)
            for key, value in sku_values.iteritems():
                row += 1
                worksheet.write(row+9, 1, key, normal_left)
                worksheet.write(row+9, 7, value, format_number_unborder)            
                total_all_sales += value
            worksheet.write(row+10 , 1, 'Total Sales (Rp)', normal_left_bold)                        
            worksheet.write(row+10 , 7, sum_total, format_number_bold_unborder)     
            worksheet.write(row+11 , 1, 'Qty of Product (Pcs)', normal_left_bold)                        
            worksheet.write(row+11 , 7, sum_qt, format_number_unborder) 
            worksheet.write(row+12 , 1, 'Total Discount (Rp)', normal_left_bold)                        
            worksheet.write(row+12 , 7, sum_disc, format_number_bold_unborder) 
            workbook.close()

            out = base64.encodestring(bz.getvalue())
            this.write({'state_x':'get', 'data_x':out, 'name': filename})

            ir_model_data = self.env['ir.model.data']
            bz.close()
            form_res = ir_model_data.get_object_reference('laporan_penjualan_promo_per_store', 'laporan_promo_per_store_report_wizard_view')
            form_id = form_res and form_res[1] or False
            
            return {
                'name': ('Download XLS'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'laporan.promo.per.store.report.wizard',
                'res_id': this.id,
                'view_id': False,
                'views': [(form_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current'
            }

