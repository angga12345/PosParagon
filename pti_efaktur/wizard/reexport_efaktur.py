import pytz
import logging
import time
from datetime import datetime, timedelta
from openerp import models, fields, api, _
from openerp.exceptions import UserError
import re
import base64
import cStringIO
import xlsxwriter
from cStringIO import StringIO
from unidecode import unidecode

_logger = logging.getLogger(__name__)

class ReexportEFaktur(models.TransientModel):
    _name = 'reexport.efaktur'
    
    state_x = fields.Selection([('choose','choose'),('get','get')], default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    delimiter = fields.Selection([(',','comma'),(';','semicolon')], string='Delimiter', default=',')
    npwp_o = fields.Boolean('NPWP000', default=False)
    
    @api.multi
    def ReexportEFaktur(self):
        data = {}
        active_ids = self.env.context.get('active_ids')
        tax_ids = self.env['dirjen.tax.code'].browse(active_ids)
        invoice_ids = [inv.invoice_id.id for inv in tax_ids if inv.invoice_id.id]
        delimiter = self.delimiter
        data['form'] = invoice_ids
        for mod in tax_ids:
            mod.npwp_o = self.npwp_o

        return self._generateEfaktur(data,delimiter)
    
    @api.multi
    def _generateEfaktur(self, data, delimiter):       
        filename = 'reexport_efaktur.csv'

        output_head = 'FK' + delimiter + 'KD_JENIS_TRANSAKSI' + delimiter + 'FG_PENGGANTI' + delimiter + 'NOMOR_FAKTUR' + delimiter + 'MASA_PAJAK' + delimiter + 'TAHUN_PAJAK' + delimiter
        output_head += 'TANGGAL_FAKTUR' + delimiter + 'NPWP' + delimiter + 'NAMA' + delimiter + 'ALAMAT_LENGKAP' + delimiter + 'JUMLAH_DPP' + delimiter + 'JUMLAH_PPN' + delimiter
        output_head +=  'JUMLAH_PPNBM' + delimiter + 'ID_KETERANGAN_TAMBAHAN' + delimiter + 'FG_UANG_MUKA' + delimiter + 'UANG_MUKA_DPP' + delimiter + 'UANG_MUKA_PPN' + delimiter + 'UANG_MUKA_PPNBM' + delimiter + 'REFERENSI'
        output_head += '\n' + 'LT' + delimiter + 'NPWP' + delimiter + 'NAMA' + delimiter + 'JALAN' + delimiter + 'BLOK' + delimiter + 'NOMOR' + delimiter
        output_head +=  'RT' + delimiter + 'RW' + delimiter + 'KECAMATAN' + delimiter + 'KELURAHAN' + delimiter + 'KABUPATEN' + delimiter + 'PROPINSI' + delimiter
        output_head +=  'KODE_POS' + delimiter + 'NOMOR_TELEPON' + delimiter + '' + delimiter + '' + delimiter + '' + delimiter + '' + delimiter + ''
        output_head += '\n' + 'OF' + delimiter + 'KODE_OBJEK' + delimiter + 'NAMA' + delimiter + 'HARGA_SATUAN' + delimiter + 'JUMLAH_BARANG' + delimiter + 'HARGA_TOTAL' + delimiter
        output_head +=  'DISKON' + delimiter + 'DPP' + delimiter + 'PPN' + delimiter + 'TARIF_PPNBM' + delimiter + 'PPNBM' + delimiter + '' + delimiter
        output_head +=  '' + delimiter + '' + delimiter + '' + delimiter + '' + delimiter + '' + delimiter + '' + delimiter + '' + '\n' #last with replace the line
        
        obj_invs = self.env['account.invoice'].browse(data['form'])
        for obj_inv in obj_invs:#browse data invoice based id dictionary
            #if state open then print invoice line
            if obj_inv.state in ('open', 'paid'): 
                invoice_number = obj_inv.dirjen_tax_id.name or ''
                invoice_date = datetime.strptime(str(obj_inv.date_invoice), "%Y-%m-%d") or False
                if not invoice_date:
                    raise UserError(_("Invoice %s no date", (invoice_number)))
                invoice_date_p = '{0}/{1}/{2}'.format(invoice_date.day, invoice_date.month, invoice_date.year) or ''
                
                invoice_npwp = ''
                if self.npwp_o == True:
                    invoice_npwp = '000000000000000'
                else:
                    invoice_npwp = obj_inv.partner_id.npwp or ''
                    invoice_npwp = invoice_npwp.replace('.', '')
                    invoice_npwp = invoice_npwp.replace('-', '')
                                    
                invoice_DPP = int(obj_inv.amount_untaxed) or ''
                invoice_PPN = int(obj_inv.amount_tax) or ''
                
                if invoice_npwp == '000000000000000' :
                    invoice_customer = obj_inv.partner_id.name
                    invoice_customer_address = obj_inv.partner_id.street or ''
                    invoice_customer_city = obj_inv.partner_id.city or ''
                    invoice_customer_state = obj_inv.partner_id.state_id.name or ''
                    invoice_customer_zip = obj_inv.partner_id.zip or ''
                    invoice_customer_country = obj_inv.partner_id.country_id.name or ''

                else :
                    invoice_customer = obj_inv.partner_id.tax_name
                    invoice_customer_address = obj_inv.partner_id.tax_address or ''
                    invoice_customer_city = ''
                    invoice_customer_state = ''
                    invoice_customer_zip = ''
                    invoice_customer_country = ''
                    if invoice_customer == False :
                        invoice_customer = ''
                        
                output_head += 'FK' + delimiter + '\"01\"' + delimiter + '0' + delimiter + '\"' + unidecode(str(invoice_number)) + '\"' + delimiter + unidecode(str(invoice_date.month)) + delimiter + unidecode(str(invoice_date.year)) + delimiter
                output_head += '\"' + unidecode(str(invoice_date_p)) + '\"' + delimiter + '\"' + unidecode(str(invoice_npwp)) + '\"' + delimiter + '\"' + unidecode(str(invoice_customer.encode('ascii',errors='ignore'))) + '\"' + delimiter + '\"' + unidecode(invoice_customer_address) + ' ' + unidecode(invoice_customer_city) + ' ' + unidecode(str(invoice_customer_state)) +' '+ unidecode(invoice_customer_zip) +' '+ unidecode(str(invoice_customer_country)) + '\"' + delimiter
                output_head += unidecode(str(invoice_DPP)) + delimiter + unidecode(str(invoice_PPN)) + delimiter + '0' + delimiter + '' + delimiter + '0' + delimiter + '0' + delimiter + '0' + delimiter + '0' + delimiter + '0' + '\n'
                
                # HOW TO ADD 2 line to 1 line for free product
                line_sorted = sorted(obj_inv.invoice_line_ids, key=lambda a: a.product_id)

                free = []
                sales = []
                for obj_inv_line in line_sorted:
                    invoice_line_default_code = obj_inv_line.product_id.default_code or ''
                    invoice_line_name = unidecode(obj_inv_line.name) or ''
                    invoice_line_unit_price = obj_inv_line.price_unit
                    invoice_line_quantity = obj_inv_line.quantity
                    invoice_line_total_price = invoice_line_unit_price * invoice_line_quantity
                    invoice_line_amount = obj_inv_line.price_subtotal
                    invoice_line_discount_m2m = invoice_line_total_price - invoice_line_amount
                    tax_line = 0
                    for tax in obj_inv_line.invoice_line_tax_ids:
                        if tax.amount > 0:
                            tax_line += invoice_line_amount * (tax.amount/100.0)
                    
                    if obj_inv_line.price_subtotal<0:
                        free.append({'default_code' : invoice_line_default_code,
                                'name' : invoice_line_name,
                                'unit_price' : invoice_line_unit_price,
                                'quantity' : invoice_line_quantity,
                                'bruto' : invoice_line_total_price,
                                'subtotal' : abs(invoice_line_amount),
                                'discount' : invoice_line_discount_m2m,
                                'ppn' : 0.0,
                                'product_id' : obj_inv_line.product_id.id,
                                })
                    else:
                        sales.append({'default_code' : invoice_line_default_code,
                                'name' : invoice_line_name,
                                'unit_price' : invoice_line_unit_price,
                                'quantity' : invoice_line_quantity,
                                'bruto' : invoice_line_total_price,
                                'subtotal' : invoice_line_amount,
                                'discount' : invoice_line_discount_m2m,
                                'ppn' : tax_line,
                                'product_id' : obj_inv_line.product_id.id,
                                })
                        
                for sale in sales:
                    for f in free:
                        if f['product_id']==sale['product_id']:
                            sale['discount'] = sale['discount'] + f['subtotal']
                            sale['subtotal'] = sale['bruto'] - sale['discount']
                            tax_line = 0
                            for tax in obj_inv_line.invoice_line_tax_ids:
                                if tax.amount > 0:
                                    tax_line += sale['subtotal']  * (tax.amount/100.0)
                            sale['ppn'] = tax_line
                            free.remove(f)
                    output_head += 'OF' + delimiter + '\"' + sale['default_code'] + '\"' + delimiter + '\"' + sale['name'] + '\"' + delimiter + '\"' + str(sale['unit_price']) + '\"' + delimiter + '\"' + str(sale['quantity']) + '\"' + delimiter + '\"' + str(sale['bruto']) + '\"' + delimiter
                    output_head += '\"' + str(int(sale['discount'])) + '\"' + delimiter + '\"' + str(sale['subtotal']) + '\"' + delimiter + '\"' + str(sale['ppn']) + '\"' + delimiter + '0' + delimiter + '0' + delimiter
                    output_head += delimiter + '' + delimiter + '' + delimiter + '' + delimiter + '' + delimiter + '' + delimiter + '' + delimiter + '' + '\n'

        my_utf8 = output_head.encode("utf-8")
        out=base64.b64encode(my_utf8)
        self.write({'state_x':'get', 'data_x':out, 'name': filename})
        ir_model_data = self.env['ir.model.data']
        form_res = ir_model_data.get_object_reference('pti_efaktur', 'view_reexport_efaktur')#module 'pti_faktur' and 'id wizard form'
        form_id = form_res and form_res[1] or False
        return {
            'name': _('Download csv'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'reexport.efaktur', #model wizard
            'res_id': self.id, #id wizard
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }
