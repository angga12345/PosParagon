from openerp import models, fields, api
from cStringIO import StringIO
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta
import xlsxwriter
import base64
import time


class LapPenjualan(models.TransientModel):
    _name="lap.penjualan.barang"

    start_period = fields.Date(string="Start Period")
    end_period = fields.Date(string="End Period")
    store = fields.Many2one('pos.config', string="store")
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    check_all = fields.Boolean('Check')
    report_type = fields.Selection([('LT', 'Laporan Retur'),
                                    ('LP', 'Laporan Penjualan'),
                                    ('LDS', 'Laporan Data Stock'),
                                    ('LSP', 'Laporan Selisih Persediaan')], string='Report Type')

    def get_data(self, start_period, end_period, store_id):
        self.env.cr.execute("""
            select rp.name, po.date_order, pp.barcode, pp.default_code,
            case
                when po.shop_identifier_origin is not null and po.shop_identifier_period is not null then po.shop_identifier_period
                when po.shop_identifier_origin is not null and po.shop_identifier_period is null then po.shop_identifier_origin
                when po.shop_identifier_origin is null and po.shop_identifier_period is not null then po.shop_identifier_period
            end as sku,
            pt.name, pol.qty, pol.price_subtotal_incl_rel / pol.qty as harga_netto,
            (pol.price_subtotal_incl_rel / pol.qty) - ((pol.price_subtotal_incl_rel / pol.qty) * (pol.discount / 100)) as discount,
            pol.price_subtotal_incl_rel
                from pos_order_line pol join pos_order po on po.id = pol.order_id
                join pos_session ps on ps.id = po.session_id
                join product_product pp on pp.id = pol.product_id
                join product_template pt on pt.id = pp.product_tmpl_id
                join res_users ru on po.user_id = ru.id
                join res_partner rp on rp.id = ru.partner_id, pos_config pc
                where po.date_order >= %s and
                po.date_order <= %s
                and pc.id = %s
            """, (start_period, end_period, store_id))
        form = self.env.cr.fetchall()
        return form

    @api.multi
    def generate_lap_penjualan(self):
        for this in self:
            start_period = this.start_period
            end_period = this.end_period
            store_id = this.store.id
            today = datetime.now() + timedelta(hours=7)
            hour  = today.strftime('%H:%M')
            sp=datetime.strptime(start_period, DEFAULT_SERVER_DATE_FORMAT)
            ep=datetime.strptime(end_period, DEFAULT_SERVER_DATE_FORMAT)
            bz = StringIO()
            workbook = xlsxwriter.Workbook(bz)

            records = this.get_data(start_period + " 00:00:00", end_period + " 23:59:59", store_id)
            filename = 'lap_penjualan.xlsx'

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

            worksheet = workbook.add_worksheet("Penjualan")
            worksheet.set_column('A:A', 5)
            worksheet.set_column('B:B', 20)
            worksheet.set_column('C:C', 18)
            worksheet.set_column('D:D', 20)
            worksheet.set_column('E:E', 20)
            worksheet.set_column('F:F', 20)
            worksheet.set_column('G:G', 20)
            worksheet.set_column('H:H', 20)
            worksheet.set_column('I:I', 10)
            worksheet.set_column('J:J', 20)
            worksheet.set_column('K:K', 10)
            worksheet.set_column('L:L', 20)
            worksheet.set_column('M:M', 20)
            worksheet.set_column('N:N', 15)
            worksheet.set_column('O:O', 15)
            worksheet.set_column('P:P', 30)
            worksheet.set_column('Q:Q', 30)
            worksheet.set_column('R:R', 15)
            worksheet.set_column('S:S', 10)
            worksheet.set_column('T:T', 15)

            worksheet.merge_range('A1:C1','Start Period : '+sp.strftime('%d %b %Y'), normal_left_bold)
            worksheet.merge_range('D1:E1','End Period : '+ep.strftime('%d %b %Y'), normal_left_bold)            
            worksheet.merge_range('F1:G1','Print Date : '+today.strftime('%d %b %Y')+', Pukul : '+hour+' WIB', normal_left_bold)
            worksheet.merge_range('A2:C2','Nama Store : '+this.store.name, normal_left_bold)
            worksheet.merge_range('A3:C3','Brand : '+this.store.tags.name, normal_left_bold)

            worksheet.write('A5', 'No.', normal_bold_border)
            worksheet.write('B5', 'Nama BA',normal_bold_border)
            worksheet.write('C5', 'Tgl Penjualan', normal_bold_border)
            worksheet.write('D5', 'Waktu Penjualan', normal_bold_border)
            worksheet.write('E5', 'Barcode', normal_bold_border)
            worksheet.write('F5', 'Kode Item', normal_bold_border)
            worksheet.write('G5', 'No SKU', normal_bold_border)
            worksheet.write('H5', 'Nama Barang', normal_bold_border)
            worksheet.write('I5', 'Qty', normal_bold_border)
            worksheet.write('J5', 'Harga Satuan(Normal)', normal_bold_border)
            worksheet.write('K5', 'Diskon', normal_bold_border)
            worksheet.write('L5', 'Harga Netto', normal_bold_border)               
            worksheet.write('M5', 'Jumlah Harga', normal_bold_border)            
            worksheet.write('N5', 'Kategori Promo', normal_bold_border)
            worksheet.write('O5', 'Periode Promo', normal_bold_border)
            worksheet.write('P5', 'Nilai Partisipasi Diskon Ditanggung PTI', normal_bold_border)
            worksheet.write('Q5', 'Nilai Partisipasi Diskon Ditanggung MDS', normal_bold_border)
            worksheet.write('R5', 'Nama Item Free', normal_bold_border)
            worksheet.write('S5', 'Qty', normal_bold_border)
            worksheet.write('T5', 'Harga Satuan', normal_bold_border)

            no = 1
            row = 5
            tot_qty = 0
            tot_price = 0
            for record in records:
                worksheet.write(row, 0, no, normal_center)
                worksheet.write(row, 1, record[0], normal_left)
                worksheet.write(row, 2, fields.Date.from_string(record[1]).strftime('%d/%m/%Y'), normal_center)
                worksheet.write(row, 3, (fields.Datetime.from_string(record[1]).strftime('%H.%M') or '') + ' WIB', normal_center)
                worksheet.write(row, 4, record[2], normal_right)
                worksheet.write(row, 5, record[3], normal_right)
                worksheet.write(row, 6, record[4], normal_right)
                worksheet.write(row, 7, record[5], normal_right)
                worksheet.write(row, 8, record[6], normal_center)
                worksheet.write(row, 9, record[7], format_number)
                worksheet.write(row, 10, record[8], format_number)
                worksheet.write(row, 11, record[9], format_number)
                worksheet.write(row, 12, record[9], format_number)
                worksheet.write(row, 13, record[9], format_number)
                no = no+1
                row = row+1
                tot_qty = tot_qty + float(record[6])
                tot_price = tot_price + float(record[7])


            worksheet.merge_range(row+1, 0, row+1, 7,'Total', normal_bold_border)
            worksheet.write(row+1, 8,'3', normal_bold_color)
            worksheet.write(row+1, 10,'3000', normal_bold_color)
            worksheet.write(row+1, 11,'300', normal_bold_color)
            worksheet.write(row+1, 12,'30', normal_bold_color)
            worksheet.write(row+1, 15,'300', normal_bold_color)
            worksheet.write(row+1, 16,'3000', normal_bold_color)
            worksheet.write(row+1, 18,'300', normal_bold_color)
            worksheet.write(row+1, 19,'30', normal_bold_color)
            workbook.close()

            out = base64.encodestring(bz.getvalue())
            this.write({'state_x':'get', 'data_x':out, 'name': filename})
 
            ir_model_data = self.env['ir.model.data']
            bz.close()
            form_res = ir_model_data.get_object_reference("pti_finance_report", "lap_penjualan_view_wizard")
            form_id = form_res and form_res[1] or False
            return {
                'name': ('Download XLS'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'lap.penjualan.barang',
                'res_id': this.id,
                'view_id': False,
                'views': [(form_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current'
            }