from openerp import models, fields, api
from cStringIO import StringIO
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta
import xlsxwriter
import base64
import time


class LapDataStock(models.TransientModel):
    _name = "lap.stok.barang"

    start_period = fields.Date(string="Start Period")
    end_period = fields.Date(string="End Period")
    store = fields.Many2one('pos.config', string="Store")
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    check_all = fields.Boolean('Check')
#         stok awal = barang masuk - barang keluar
#         barang masuk = ke lokasi pos store
#         barang keluar = dari lokasi pos store
#         kirim barang = from DC to Pos Store
#         retur = from Pos Store to DC
#         jual free = 100%
    def get_data(self, start_period, end_period, location_id, dc_location_id, config_id):
        self.env.cr.execute("""
                select pp.default_code, pp.barcode, pt.name,
                (select sum(product_uom_qty) from stock_move where
                    location_dest_id = %s and state = 'done' and
                    product_id = sm.product_id and date < %s group by product_id) - 
                (select sum(product_uom_qty) from stock_move where
                    location_id = %s and state = 'done' and product_id = sm.product_id
                    and date < %s group by product_id) as saldo_awal,
                (select sum(product_uom_qty) from stock_move where
                    location_dest_id = %s and state = 'done' and product_id = sm.product_id
                    group by product_id) as kirim_barang,
                (select sum(product_uom_qty) from stock_move where
                    location_id = %s and location_dest_id = %s and state = 'done' and
                    product_id = sm.product_id group by product_id) as retur,
                (select sum(qty) from pos_order_line pol join pos_order po on po.id = pol.order_id 
                    join pos_session ps on ps.id = po.session_id
                    join pos_config pc on pc.id = ps.config_id
                    where pc.id = %s and pol.discount < 100
                    and pol.product_id = sm.product_id) as penjualan,
                (select sum(qty) from pos_order_line pol join pos_order po on po.id = pol.order_id 
                    join pos_session ps on ps.id = po.session_id
                    join pos_config pc on pc.id = ps.config_id
                    where pc.id = %s and pol.discount = 100
                    and pol.product_id = sm.product_id) as jual_free,
                round(pt.list_price + (pt.list_price * (
                    (select act.amount from product_taxes_rel ptr, product_template pt, account_tax act
                        where ptr.prod_id = pt.id and act.id = tax_id and pt.id = sm.product_id)/100)
                    ), 0) as harga_satuan
                from stock_move sm
                join product_product pp on pp.id = sm.product_id
                join product_template pt on pt.id = pp.product_tmpl_id
                where location_dest_id = %s and sm.state = 'done'
                and date > %s and date < %s
                group by product_id, sm.id, pt.name, pp.barcode, pp.default_code, pt.list_price
                """, (location_id, start_period, # stock awal
                      location_id, start_period, # stock awal
                      location_id, # kirim barang
                      location_id, dc_location_id, # retur
                      config_id, # penjualan
                      config_id, # jual free
                      location_id,
                      start_period, end_period))

        form = self.env.cr.fetchall()
        return form

    def get_dc_location(self, dc):
        stock_location_obj = self.env['stock.location']
        location_id = stock_location_obj.search([('dc_id', '=', dc.id), ('partner_id', '=', dc.id), ('name', '=ilike', 'stock')], limit=1)
        return location_id

    def get_dc(self, location_id):
        return location_id.dc_id

    @api.multi
    def generate_lap_data_stock(self):
        for this in self:
            start_period = this.start_period
            end_period = this.end_period
            location_id = this.store.stock_location_id
            today = datetime.now() + timedelta(hours=7)
            hour = today.strftime('%H:%M')
            sp = datetime.strptime(start_period, DEFAULT_SERVER_DATE_FORMAT)
            ep = datetime.strptime(end_period, DEFAULT_SERVER_DATE_FORMAT)
            bz = StringIO()
            workbook = xlsxwriter.Workbook(bz)
            print location_id.id
            distribution_center = self.get_dc(location_id)
            location_dest_id = self.get_dc_location(distribution_center)
            records = this.get_data(start_period + " 00:00:00", end_period + " 23:59:59", location_id.id, location_dest_id.id, this.store.id)

            filename = 'lap_data_stock.xlsx'

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
            normal_center = workbook.add_format({'valign':'bottom','align':'center'})
            normal_center.set_text_wrap()
            normal_center.set_font_name('Arial')
            normal_center.set_font_size('10')
            #################################################################################
            normal_right = workbook.add_format({'valign':'bottom','align':'right'})
            normal_right.set_text_wrap()
            normal_right.set_font_name('Arial')
            normal_right.set_font_size('10')
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
            normal_border = workbook.add_format({'valign':'vcenter','align':'center'})
            normal_border.set_text_wrap()
            normal_border.set_font_name('Arial')
            normal_border.set_font_size('10')
            normal_border.set_border()
            #################################################################################
            normal_bold_color = workbook.add_format({'bold': 1,'valign':'vcenter','align':'center'})
            normal_bold_color.set_text_wrap()
            normal_bold_color.set_font_name('Arial')
            normal_bold_color.set_font_size('10')
            normal_bold_color.set_border()
            normal_bold_color.set_bg_color('yellow')
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

            worksheet = workbook.add_worksheet("Data Stok")
            worksheet.set_column('A:A', 5)
            worksheet.set_column('B:B', 15)
            worksheet.set_column('C:C', 18)
            worksheet.set_column('D:D', 20)
            worksheet.set_column('E:E', 20)
            worksheet.set_column('F:F', 20)
            worksheet.set_column('G:G', 20)
            worksheet.set_column('H:H', 20)
            worksheet.set_column('I:I', 25)
            worksheet.set_column('J:J', 20)
            worksheet.set_column('K:K', 20)
            worksheet.set_column('L:L', 20)

            worksheet.merge_range('A1:C1','Start Period : '+sp.strftime('%d %b %Y'), normal_left_bold)
            worksheet.merge_range('D1:E1','End Period : '+ep.strftime('%d %b %Y'), normal_left_bold)            
            worksheet.merge_range('F1:G1','Print Date : '+today.strftime('%d %b %Y')+', Pukul : '+hour+' WIB', normal_left_bold)
            worksheet.merge_range('A2:C2','Nama Store : '+this.store.name, normal_left_bold)
            worksheet.merge_range('A3:C3','Brand : ', normal_left_bold)

            worksheet.write('A5', 'No.', normal_bold_border)
            worksheet.write('B5', 'Barcode',normal_bold_border)
            worksheet.write('C5', 'Kode Item', normal_bold_border)
            worksheet.write('D5', 'Nama Item', normal_bold_border)
            worksheet.write('E5', 'Saldo Awal', normal_bold_border)
            worksheet.write('F5', 'Kirim Barang', normal_bold_border)
            worksheet.write('G5', 'Retur', normal_bold_border)
            worksheet.write('H5', 'Penjualan', normal_bold_border)
            worksheet.write('I5', 'Barang Jual Untuk Free', normal_bold_border)
            worksheet.write('J5', 'Stok Akhir', normal_bold_border)
            worksheet.write('K5', 'Harga Satuan', normal_bold_border)
            worksheet.write('L5', 'Jumlah Harga', normal_bold_border)               

            no = 1
            row = 5
            tot_saldo_awal = 0
            tot_kirim_barang = 0
            tot_retur = 0
            tot_penjualan = 0
            tot_jual_free = 0
            tot_stock_akhir = 0
            tot_harga = 0
            for record in records:
                stok_akhir = ((record[3] or 0) + (record[4] or 0)) - ((record[5] or 0) + (record[6] or 0) + (record[7] or 0))
                worksheet.write(row, 0, no, normal_border)
                worksheet.write(row, 1, record[1], normal_border)
                worksheet.write(row, 2, record[0], normal_border)
                worksheet.write(row, 3, record[2], normal_border)
                worksheet.write(row, 4, record[3], normal_border)
                worksheet.write(row, 5, record[4], normal_border)
                worksheet.write(row, 6, record[5], normal_border)
                worksheet.write(row, 7, record[6], normal_border)
                worksheet.write(row, 8, record[7], normal_border)
                worksheet.write(row, 9, stok_akhir, normal_border)
                worksheet.write(row, 10, record[8], normal_border)
                worksheet.write(row, 11, stok_akhir * (record[8] or 0), format_number)
                no = no+1
                row = row+1
                tot_saldo_awal = tot_saldo_awal + float(record[4] or 0)
                tot_kirim_barang = tot_kirim_barang + float(record[4] or 0)
                tot_retur = tot_retur + float(record[4] or 0)
                tot_penjualan = tot_penjualan + float(record[4] or 0)
                tot_jual_free = tot_jual_free + float(record[4] or 0)
                tot_stock_akhir = tot_stock_akhir + float(record[4] or 0)
                tot_harga = tot_harga + float(record[4] or 0)

            worksheet.merge_range(row+1, 0, row+1, 3, 'Total', normal_bold_border)
            worksheet.write(row+1, 4, tot_saldo_awal, normal_bold_color)
            worksheet.write(row+1, 5, tot_kirim_barang, normal_bold_color)
            worksheet.write(row+1, 6, tot_retur, normal_bold_color)
            worksheet.write(row+1, 7, tot_penjualan, normal_bold_color)
            worksheet.write(row+1, 8, tot_jual_free, normal_bold_color)
            worksheet.write(row+1, 9, tot_stock_akhir, normal_bold_color)
            worksheet.write(row+1, 11, tot_harga, normal_bold_color)
            workbook.close()

            out = base64.encodestring(bz.getvalue())
            this.write({'state_x':'get', 'data_x':out, 'name': filename})
 
            ir_model_data = self.env['ir.model.data']
            bz.close()
            form_res = ir_model_data.get_object_reference("pti_finance_report", "lap_data_stok_view_wizard")
            form_id = form_res and form_res[1] or False
            return {
                'name': ('Download XLS'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'lap.stok.barang',
                'res_id': this.id,
                'view_id': False,
                'views': [(form_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current'
            }