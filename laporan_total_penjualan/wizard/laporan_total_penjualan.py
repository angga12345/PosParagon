from openerp import models, fields, api
from cStringIO import StringIO
from datetime import datetime
import xlsxwriter
import base64


class LaporanTotalPenjualanReportWizard(models.TransientModel):
    _name = "laporan.total.penjualan.report.wizard"

    start_period = fields.Date(string="Start Period")
    end_period = fields.Date(string="End Period")
    store_name = fields.Many2one("pos.config", string="Store",
                                 domain=[('category_shop', '=', 'stand_alone'),
                                         ('stand_alone_categ', '=', 'wbh')])
    state_x = fields.Selection((('choose', 'choose'), ('get', 'get')), default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    check_all=fields.Boolean('Check')

    @api.multi
    def generate_excel(self):
        for this in self:
            start_period = this.start_period
            end_period = this.end_period
            today = datetime.now()
            sp = datetime.strptime(start_period, '%Y-%m-%d')
            ep = datetime.strptime(end_period, '%Y-%m-%d')
            sn = self.store_name.name
            sn_id = self.store_name.id


            bz = StringIO()
            workbook = xlsxwriter.Workbook(bz)
            
            # ba = self.env['pos.order'].search([('user_id','=','BA 1')])
            # print "BA",ba

            filename = 'WBH Laporan Total Penjualan Per Store '+self.store_name.name+'.xls'
            print "filename",filename


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
            normal_center_bold = workbook.add_format({'bold' :1, 'valign':'bottom','align':'left'})
            normal_center_bold.set_font_name('Arial')
            normal_center_bold.set_font_size('10')
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
            normal_center_border = workbook.add_format({'valign':'center','align':'center'})
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
            
            worksheet = workbook.add_worksheet("Penj. Total Harian")
            worksheet.set_column('A:A', 5)
            worksheet.set_column('B:B', 22)
            worksheet.set_column('C:C', 17)
            worksheet.set_column('D:D', 16)
            
            worksheet.merge_range('A1:D1', 'Laporan Total Penjualan '+self.store_name.name, center_title)
            stringSN = 'Store Name : '+sn
            worksheet.write('A3',stringSN ,normal_left_bold)
            worksheet.write('B4','Start Period :',normal_left_bold)
            worksheet.write('B5', sp.strftime('%d %b %Y'),normal_left)
            worksheet.write('C4', 'End Period :',normal_center_bold)
            worksheet.write('C5', ep.strftime('%d %b %Y'),normal_left) 
            worksheet.write('D4', 'Print Date :',normal_left_bold)
            worksheet.write('D5', today.strftime('%d %b %Y %H:%M'),normal_left) 
            
            worksheet.merge_range('A6:A7', 'No.', normal_bold_border)
            worksheet.merge_range('B6:B7', 'Nama BA', normal_bold_border)
            worksheet.merge_range('C6:D6', 'Total Penjualan', normal_bold_border)
            worksheet.write('C7', 'Produk', normal_bold_border)
            worksheet.write('D7', 'Treatment', normal_bold_border)

            self.env.cr.execute("""
                select distinct
                            rpartner.name as nama_ba,
                            sum(case when ptemplate.type = 'product' then price_subtotal_incl_rel else 0 end),
                            sum(case when ptemplate.type = 'service' then price_subtotal_incl_rel else 0 end)
                        from 
                            pos_order as porder
                        join 
                            pos_order_line as pline on porder.id = pline.order_id 
                        join 
                            res_users rusers on porder.user_id = rusers.id
                        join 
                            res_partner rpartner on rusers.partner_id = rpartner.id 
                        join 
                            product_product as pproduct on pproduct.id = pline.product_id
                        join 
                            product_template as ptemplate on pproduct.product_tmpl_id = ptemplate.id
                        join     
                            pos_session as psession on porder.session_id = psession.id
                        join 
                            pos_config as pconfig on psession.config_id = pconfig.id                    
                        where 
                            pconfig.id = %s AND
                            porder.date_order >= %s AND
                            porder.date_order <= %s
                        group by 
                            rpartner.name
                """,(sn_id, start_period+" 00:00:00", end_period+" 23:59:59"))
            
            obj_pos = self.env.cr.fetchall()
            row=1
            incP = 0
            sum_produk    = 0.0
            sum_treatment = 0.0

            for pos in obj_pos:
                worksheet.write(row+6, 0, row, normal_center_border)
                worksheet.write(row+6, 1, pos[0], normal_left_border)
                worksheet.write(row+6, 2, pos[1], format_number)
                worksheet.write(row+6, 3, pos[2], format_number)
                nama_ba = pos[0]
                sum_produk += pos[1]
                sum_treatment += pos[2]

                row += 1
                
                if len(obj_pos)-1==incP:
                    stringMerge='A'+str((row+6)+1)+':B'+str((row+6)+1)
    #                     print stringMerge
                    worksheet.merge_range(stringMerge, 'TOTAL', normal_bold_border)
                    worksheet.write(row+6 , 2, sum_produk, format_number_bold)
                    worksheet.write(row+6 , 3, sum_treatment, format_number_bold)                   
                incP += 1

            workbook.close()

            out = base64.encodestring(bz.getvalue())
            this.write({'state_x':'get', 'data_x':out, 'name': filename})

            ir_model_data = self.env['ir.model.data']
            bz.close()
            form_res = ir_model_data.get_object_reference('laporan_total_penjualan', 'laporan_total_penjualan_report_wizard_view')
            form_id = form_res and form_res[1] or False                                             
            
            return {
                'name': ('Download XLS'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'laporan.total.penjualan.report.wizard',
                'res_id': this.id,
                'view_id': False,
                'views': [(form_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'current'
            }

