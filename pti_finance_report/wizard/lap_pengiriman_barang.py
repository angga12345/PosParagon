from openerp import models, fields, api
from cStringIO import StringIO
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta
import xlsxwriter
import base64
import time


class LapPengirimanBarang(models.TransientModel):
    _name = "lap.pengiriman.barang"

    start_period = fields.Date(string="Start Period")
    end_period = fields.Date(string="End Period")
    store = fields.Many2one('pos.config', string="Store")
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    check_all = fields.Boolean('Check')

    def get_data(self, start_period, end_period, location_id):
        self.env.cr.execute("""
            select sp.name, sp.date, pp.default_code, pp.barcode, pp.name_template, round(((pt.list_price * (act.amount / 100)) + pt.list_price), 0), spo.product_uom_qty,
                round(spo.product_uom_qty * ((pt.list_price * (act.amount / 100)) + pt.list_price), 0), rp.name, ru_p.name, sp.create_date, sp.date_shipment_picking 
                from stock_move spo join stock_picking sp on spo.picking_id = sp.id 
                join truck_picking_shipment st on sp.tracking_id = st.id
                left join res_partner rp on rp.id = st.partner_id
                join res_users ru on ru.id = st.user_id
                join res_partner ru_p on ru_p.id = ru.partner_id
                join product_product pp on spo.product_id = pp.id
                join product_template pt on pp.product_tmpl_id = pt.id,
                account_tax act, product_taxes_rel ptr
                where sp.location_dest_id = %s
                and sp.state = 'done'
                and sp.min_date >= %s
                and sp.min_date <= %s
                and ptr.prod_id = pt.id and act.id = ptr.tax_id
                """, (location_id, start_period, end_period))

        form = self.env.cr.fetchall()
        print form
        return form

    @api.multi
    def generate_pengiriman_barang(self):
        for this in self:
            start_period = this.start_period
            end_period = this.end_period
            location_id = this.store.stock_location_id.id
            today = datetime.now()
            sp = datetime.strptime(start_period, DEFAULT_SERVER_DATE_FORMAT)
            ep = datetime.strptime(end_period, DEFAULT_SERVER_DATE_FORMAT)
            bz = StringIO()
            workbook = xlsxwriter.Workbook(bz)

            records = this.get_data(start_period + " 00:00:00", end_period + " 23:59:59", location_id)

            filename = 'lap_pengiriman_barang.xlsx'

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
            format_number = workbook.add_format({'bold':1, 'valign':'vcenter','align':'right'})
            format_number.set_num_format('#,##0.00')
            format_number.set_font_name('Arial')
            format_number.set_font_size('10')
            format_number.set_border()
            #################################################################################
            format_number_color = workbook.add_format({'bold': 1,'valign':'vcenter','align':'center'})
            format_number_color.set_num_format('#,##0.00')
            format_number_color.set_text_wrap()
            format_number_color.set_font_name('Arial')
            format_number_color.set_font_size('10')
            format_number_color.set_border()
            format_number_color.set_bg_color('yellow')

            worksheet = workbook.add_worksheet("pengiriman barang")
            worksheet.set_column('A:A', 5)
            worksheet.set_column('B:B', 15)
            worksheet.set_column('C:C', 15)
            worksheet.set_column('D:D', 20)
            worksheet.set_column('E:E', 20)
            worksheet.set_column('F:F', 20)
            worksheet.set_column('G:G', 20)
            worksheet.set_column('H:H', 20)
            worksheet.set_column('I:I', 15)
            worksheet.set_column('J:J', 10)
            worksheet.set_column('K:K', 10)
            worksheet.set_column('L:L', 5)
            worksheet.set_column('M:M', 10)
            worksheet.set_column('N:N', 15)

            worksheet.merge_range('A1:C1', 'Start Period : '+sp.strftime('%d %b %Y'), normal_left_bold)
            worksheet.merge_range('D1:E1', 'End Period : '+ep.strftime('%d %b %Y'), normal_left_bold)            
            worksheet.merge_range('F1:G1', 'Print Period : '+today.strftime('%d %b %Y')+', Pukul ' +today.strftime('%h:%m:%s'), normal_left_bold)
            worksheet.merge_range('A2:C2', 'Nama Store : '+this.store.name, normal_left_bold)
            worksheet.merge_range('A3:C3', 'Brand : '+ this.store.tags.name, normal_left_bold)

            worksheet.write('A5', 'No.', normal_bold_border)
            worksheet.write('B5', 'No DO', normal_bold_border)
            worksheet.write('C5', 'Tgl DO', normal_bold_border)
            worksheet.write('D5', 'Tgl Terima Barang', normal_bold_border)
            worksheet.write('E5', 'Nama Driver', normal_bold_border)
            worksheet.write('F5', 'Nama BA', normal_bold_border)
            worksheet.write('G5', 'Tgl Input Barang', normal_bold_border)
            worksheet.write('H5', 'Jam Input Barang', normal_bold_border)
            worksheet.write('I5', 'No Barcode', normal_bold_border)
            worksheet.write('J5', 'Kode Item', normal_bold_border)
            worksheet.write('K5', 'Nama Item', normal_bold_border)
            worksheet.write('L5', 'Qty', normal_bold_border)
            worksheet.write('M5', 'Harga Satuan', normal_bold_border)
            worksheet.write('N5', 'Jumlah Harga', normal_bold_border)

            no = 1
            row = 5
            tot_qty = 0
            tot_price = 0
            for record in records:
                worksheet.write(row, 0, no, normal_bold_border)
                worksheet.write(row, 1, record[0], normal_bold_border)
                worksheet.write(row, 2, fields.Date.from_string(record[1]).strftime('%d/%m/%Y'), normal_bold_border)
                worksheet.write(row, 3, fields.Date.from_string(record[11]).strftime('%d/%m/%Y') if record[11] else '', normal_bold_border)
                worksheet.write(row, 4, record[8], normal_bold_border)
                worksheet.write(row, 5, record[9], normal_bold_border)
                worksheet.write(row, 6, fields.Datetime.from_string(record[10]).strftime('%d/%m/%Y'), normal_bold_border)
                worksheet.write(row, 7, (fields.Datetime.from_string(record[10]).strftime('%H.%M') or '') + ' WIB', normal_bold_border)
                worksheet.write(row, 8, record[3], normal_bold_border)
                worksheet.write(row, 9, record[2], normal_bold_border)
                worksheet.write(row, 10, record[4], normal_bold_border)
                worksheet.write(row, 11, record[6], normal_bold_border)
                worksheet.write(row, 12, record[5], format_number)
                worksheet.write(row, 13, record[7], format_number)
                row = row+1
                tot_qty = tot_qty + float(record[6])
                tot_price = tot_price + float(record[7])

            worksheet.merge_range(row+1, 0, row+1, 10, 'Total', normal_bold_border)
            worksheet.write(row+1, 11, tot_qty, normal_bold_color)
            worksheet.write(row+1, 13, tot_price, format_number_color)
            workbook.close()

            out = base64.encodestring(bz.getvalue())
            this.write({'state_x': 'get', 'data_x': out, 'name': filename})

            ir_model_data = self.env['ir.model.data']
            bz.close()
            form_res = ir_model_data.get_object_reference("pti_finance_report", "lap_pengiriman_barang_view_wizard")
            form_id = form_res and form_res[1] or False
            return {
                'name': ('Download XLS'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'lap.pengiriman.barang',
                'res_id': this.id,
                'view_id': False,
                'views': [(form_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current'
            }