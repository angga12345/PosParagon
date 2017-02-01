from openerp import models, fields, api
from cStringIO import StringIO
from datetime import datetime, timedelta
import xlsxwriter
import base64
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
from xlsxwriter.utility import xl_rowcol_to_cell

    
class MdsSalesHarianMingguan(models.TransientModel):
    _name = "mds.sales.harian.mingguan.wizard"

    store = fields.Many2one('pos.config', string="Store")
    start_period = fields.Date(string="Start Period")
    end_period = fields.Date(string="End Period")
    store_name = fields.Many2one("pos.config", string="Store", domain=[('category_shop', '=','stand_alone')])
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
        sp=datetime.strptime(start_period, '%Y-%m-%d')
        ep=datetime.strptime(end_period, '%Y-%m-%d')
        sn = self.store_name.name
        
        bz = StringIO()
        workbook = xlsxwriter.Workbook(bz)

        filename = 'Lap Total Penjualan.xlsx'

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
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 25)
        
        row=0
        worksheet.merge_range('E1:H1', 'Laporan Total Penjualan', center_title)
        worksheet.write('A3', 'Start Period:', normal_left_bold)
        worksheet.write('A4', sp.strftime('%d %b %Y'), normal_left_unborder)
        worksheet.write('B3', 'End Period :', normal_left_bold)
        worksheet.write('B4', ep.strftime('%d %b %Y'),normal_left_unborder) 
        worksheet.write('C3', 'Print Date :', normal_left_bold)
        worksheet.write('C4', today.strftime('%d %b %Y %H:%M'), normal_left_unborder)
        
        worksheet.merge_range('A5:A7', 'DC', normal_bold_border)
        worksheet.merge_range('B5:B7', 'Brand', normal_bold_border)
        worksheet.merge_range('C5:C7', 'Store Name', normal_bold_border)

        from datetime import timedelta, date

        def daterange(start_date, end_date):
            for n in range(int((datetime.strptime(end_date,'%Y-%m-%d')-datetime.strptime(start_date,'%Y-%m-%d')).days)+1):
                yield datetime.strptime(start_date,'%Y-%m-%d') + timedelta(n)
                
        list_date=daterange(start_period,end_period)    
        
        def reversed_iterator(lst_iter):
            return reversed(list(lst_iter))
        
        cc=reversed_iterator(list_date)
        
        c=3
        d=4
        for single_date in cc:
            worksheet.merge_range(row+4,c,row+4,d,single_date.strftime("%d %b %Y"), normal_bold_border)
            worksheet.merge_range(row+5,c,row+5,d,'Total Penjualan', normal_bold_border)
            worksheet.write(row+6,c,'Produk', normal_bold_border)
            worksheet.write(row+6,d,'Treatment', normal_bold_border)
            c+=2
            d+=2
        worksheet.merge_range(row+4,c,row+4,d,'TOTAL', normal_bold_border)
        worksheet.merge_range(row+5,c,row+5,d,'Total Penjualan', normal_bold_border)
        worksheet.write(row+6,c,'Produk', normal_bold_border)
        worksheet.write(row+6,d,'Treatment', normal_bold_border)
        worksheet.set_column(c,c, 15)
        
        worksheet.freeze_panes(8,4)

        #LOOPING DC,BRAND,NAMA TOKO
        self.env.cr.execute("""
            select dcpartner.name as dc, pbrand.name as brand, pconfig.name as shop, ptemplate.type, date(porder.date_order),
                    coalesce(sum(pline.price_subtotal_rel),0) as total
                    from pos_order porder join pos_order_line pline on porder.id = pline.order_id 
                        join pos_session psession on porder.session_id = psession.id
                        join pos_config pconfig on psession.config_id = pconfig.id
                        join product_product pproduct on pproduct.id = pline.product_id
                        join stock_location slocation on slocation.id = pconfig.stock_location_id
                        join res_partner rpartner on rpartner.id = slocation.partner_id
                        join res_partner dcpartner on rpartner.dc_id = dcpartner.id 
                        join product_brand pbrand on pbrand.id = pconfig.tags
                        join product_template ptemplate on pproduct.product_tmpl_id = ptemplate.id
                    where porder.date_order >= %s AND porder.date_order <= %s AND pconfig.name = %s
                    group by date(porder.date_order), ptemplate.type, pbrand.name, dcpartner.name, pconfig.name
                    order by dcpartner.name, pbrand.name, pconfig.name asc
                    """, (self.start_period+' 00:00:00', end_period+' 23:59:59', sn))
        brand = {}
        q1 = self.env.cr.fetchall()
        for q in q1:               
            if q[0] in brand:
                if q[1] in brand[q[0]]:
                    if q[2] in brand[q[0]][q[1]]:
                        brand[q[0]][q[1]][q[2]].append(q[4])
                    else:
                        brand[q[0]][q[1]][q[2]] = []
                else:
                    brand[q[0]][q[1]] = {}
            else:
                brand[q[0]] = {}
                brand[q[0]][q[1]] = {}
                brand[q[0]][q[1]][q[2]] = []
                brand[q[0]][q[1]][q[2]].append(q[4])

        total_prod = 0
        total_serv = 0
        tot_total_prod = 0
        tot_total_serv = 0
        row=0
        for key, value in brand.iteritems():       
            for k, v in value.iteritems():
                tot_pbrand = -1
                for k1, v1 in v.iteritems():
                    pbrand = len(v)
                    tot_pbrand += pbrand
                    
                    worksheet.write(row+7, 0, "", normal_left)
                    worksheet.write(row+7 , 2, k1, normal_left)
                    #LOOPING TANGGAL 1
                    dt=daterange(start_period, end_period)
                    cc_2 = reversed_iterator(dt)
                    e = 3
                    f = 4
                    for m in cc_2:
                        self.env.cr.execute("""
                            set datestyle=dmy;
                            select pbrand.name as brand, dcpartner.name as dc, pconfig.name as shop, ptemplate.type, date(porder.date_order),
                                coalesce(sum(pline.price_subtotal_rel),0) as total
                                from pos_order porder join pos_order_line pline on porder.id = pline.order_id 
                                    join pos_session psession on porder.session_id = psession.id
                                    join pos_config pconfig on psession.config_id = pconfig.id
                                    join product_product pproduct on pproduct.id = pline.product_id
                                    join stock_location slocation on slocation.id = pconfig.stock_location_id
                                    join res_partner rpartner on rpartner.id = slocation.partner_id
                                    join res_partner dcpartner on rpartner.dc_id = dcpartner.id 
                                    join product_brand pbrand on pbrand.id = pconfig.tags
                                    join product_template ptemplate on pproduct.product_tmpl_id = ptemplate.id
                                where pconfig.name = %s AND porder.date_order >= %s AND porder.date_order <= %s
                                group by date(porder.date_order), ptemplate.type, pbrand.name, dcpartner.name, pconfig.name
                                order by pbrand.name, dcpartner.name, pconfig.name asc
                                """, (k1, m.strftime("%d-%m-%y")+' 00:00:00', m.strftime("%d-%m-%y")+' 23:59:59'))
                        obj_pos = self.env.cr.fetchall()
                        print 'hm?',obj_pos
                        if obj_pos:
                            for n in obj_pos:
                                if n[3] == 'product':
                                    worksheet.write(row+7,e,n[5], format_number)
                                    total_prod += n[5]   
                                elif n[3] == 'service':
                                    worksheet.write(row+7,f,n[5], format_number)
                                    total_serv += n[5]
                                else:
                                    worksheet.write(row+7,e, "", format_number)
                                    worksheet.write(row+7,f, "", format_number)
                        else:
                            worksheet.write(row+7,e, "", format_number)
                            worksheet.write(row+7,f, "", format_number)
                        e += 2
                        f += 2
                    
                    
                    worksheet.write(row+7,e, total_prod, format_number_bold)
                    tot_total_prod += total_prod
                    worksheet.write(row+7,f, total_serv, format_number_bold)
                    tot_total_serv += total_serv

                    worksheet.write(row+8,e, tot_total_prod, format_number_bold)
                    worksheet.write(row+8,f, tot_total_serv, format_number_bold)

                    
        #DC           
        if tot_pbrand>=1 :
             worksheet.write(0+7, 0, 0+7+tot_pbrand-1, 0, key, normal_left)
        else :
             worksheet.write(0+7 , 0, key, normal_left)
             
        
        
        #Brand    
        if pbrand>1 :
            worksheet.merge_range(0+7 , 1, 0+7+pbrand-1, 1, k, normal_left)
        else :
            worksheet.write(0+7 , 1, k, normal_left)
        
        row += 1
            
        #LOOPING GRAND TOTAL PRODUK
        grand_day=daterange(start_period, end_period)
        cc_grandday=reversed_iterator(grand_day)
        granddt=0
        gdt_totday_prod=0
        for o in cc_grandday:
            self.env.cr.execute("""
            set datestyle=dmy;
            select  ptemplate.type, date(porder.date_order),
                coalesce(sum(pline.price_subtotal_rel),0) as total
                from pos_order porder join pos_order_line pline on porder.id = pline.order_id 
                    join pos_session psession on porder.session_id = psession.id
                    join pos_config pconfig on psession.config_id = pconfig.id
                    join product_product pproduct on pproduct.id = pline.product_id
                    join stock_location slocation on slocation.id = pconfig.stock_location_id
                    join res_partner rpartner on rpartner.id = slocation.partner_id
                    join res_partner dcpartner on rpartner.dc_id = dcpartner.id 
                    join product_brand pbrand on pbrand.id = pconfig.tags
                    join product_template ptemplate on pproduct.product_tmpl_id = ptemplate.id
                where ptemplate.type = 'product' and porder.date_order >= %s AND porder.date_order <= %s
                group by date(porder.date_order), ptemplate.type
                """, (o.strftime("%d-%m-%y")+' 00:00:00',o.strftime("%d-%m-%y")+' 23:59:59'))
            totalday=self.env.cr.fetchall()
            if totalday:
                worksheet.write(row+7,3+granddt, totalday[0][2], format_number_bold)
                gdt_totday_prod+=totalday[0][2]
            else:
                worksheet.write(row+7,3+granddt, "", format_number_bold) 
            granddt+=2

         #LOOPING GRAND TOTAL SERVIS
        grand_day2=daterange(start_period, end_period)
        cc_grandday2=reversed_iterator(grand_day2)
        granddt2=0
        gdt_totday_serv=0
        for o in cc_grandday2:
            self.env.cr.execute("""
            set datestyle=dmy;
            select  ptemplate.type, date(porder.date_order),
                coalesce(sum(pline.price_subtotal_rel),0) as total
                from pos_order porder join pos_order_line pline on porder.id = pline.order_id 
                    join pos_session psession on porder.session_id = psession.id
                    join pos_config pconfig on psession.config_id = pconfig.id
                    join product_product pproduct on pproduct.id = pline.product_id
                    join stock_location slocation on slocation.id = pconfig.stock_location_id
                    join res_partner rpartner on rpartner.id = slocation.partner_id
                    join res_partner dcpartner on rpartner.dc_id = dcpartner.id 
                    join product_brand pbrand on pbrand.id = pconfig.tags
                    join product_template ptemplate on pproduct.product_tmpl_id = ptemplate.id
                where ptemplate.type = 'service' and porder.date_order >= %s AND porder.date_order <= %s
                group by date(porder.date_order), ptemplate.type
                """, (o.strftime("%d-%m-%y")+' 00:00:00',o.strftime("%d-%m-%y")+' 23:59:59'))
            totalday2=self.env.cr.fetchall()
            if totalday2:
                worksheet.write(row+7,4+granddt2, totalday2[0][2], format_number_bold)
                gdt_totday_serv+=totalday2[0][2]
            else:
                worksheet.write(row+7,4+granddt2, "", format_number_bold)
            granddt2+=2

        worksheet.merge_range('B'+str(row+8)+':C'+str(row+8), "TOTAL", normal_bold_border)
        
        workbook.close()

        out = base64.encodestring(bz.getvalue())
        self.write({'state_x':'get', 'data_x':out, 'name': filename})

        ir_model_data = self.env['ir.model.data']
        bz.close()
        form_res = ir_model_data.get_object_reference('pti_mds_sales_harian_mingguan', 'mds_sales_harian_mingguan_wizard_view')
        form_id = form_res and form_res[1] or False
        
        return {
            'name': ('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mds.sales.harian.mingguan.wizard',
            'res_id': self.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }


