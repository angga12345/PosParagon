# Copyright (C) 2016 by PT Paragon Technology And Innovation
#
# This file is part of PTI Odoo Addons.
#
# PTI Odoo Addons is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PTI Odoo Addons is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with PTI Odoo Addons.  If not, see <http://www.gnu.org/licenses/>.

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

_logger = logging.getLogger(__name__)

class e_faktur_report(models.TransientModel):
    _name = "efaktur.report"
    
    start_date = fields.Date('Start date')
    end_date = fields.Date('End date')
    state_x = fields.Selection([('choose','choose'),('get','get')])
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    
    _defaults = {
        'state_x': lambda *a: 'choose',
    }
    
    number_format = False
    bold_with_border = False
    
    @api.model
    def set_width(self, worksheet):
        worksheet.set_column('A1:A1', 5)
        worksheet.set_column('B1:B1', 20)
        worksheet.set_column('C1:C1', 40)
        worksheet.set_column('D1:D1', 25)
        worksheet.set_column('E1:E1', 20)
        return worksheet
        
    @api.model
    def add_workbook_format(self, workbook):
        self.bold_with_border = workbook.add_format({})
        self.bold_with_border.set_border()
        
        self.number_format = workbook.add_format({'align': 'right','num_format': '#,##0.00'})
        self.number_format.set_border()
        return workbook
        
    @api.multi
    def create_efaktur_report(self):
        data = {}
        data['start_date'] = self.start_date
        data['end_date'] = self.end_date 
        return self._print_efaktur_report_general(data)
    
    @api.multi
    def _print_efaktur_report_general(self, data):
        filename = 'efaktur_general_report.xlsx'
        fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)
        workbook = self.add_workbook_format(workbook)
        serial_number = self.env['dirjen.tax.code'].search([
                                            ('date_validated','>=',data['start_date']),
                                            ('date_validated','<=',data['end_date']),
                                            ('validated','=',True)])
        
        worksheet = workbook.add_worksheet("Report Efaktur")
        worksheet.hide_gridlines(1)
        worksheet = self.set_width(worksheet)

        worksheet.merge_range('A1:C1', data['start_date']+ " s/d " + data['end_date'], self.bold_with_border)
        
        worksheet.write(1, 0, "No.", self.bold_with_border)
        worksheet.write(1, 1, "Nomor Invoice", self.bold_with_border)
        worksheet.write(1, 2, "Customer", self.bold_with_border)
        worksheet.write(1, 3, "Serial Number", self.bold_with_border)
        worksheet.write(1, 4, "Amount(without tax)", self.bold_with_border)
        
        baris = 2
        nomor = 1
        for data_efaktur in serial_number:
            if 'PRM/' not in data_efaktur.invoice_id.number:
                worksheet.write(baris, 0, nomor , self.bold_with_border)
                worksheet.write(baris, 1, data_efaktur.invoice_id.number , self.bold_with_border)
                worksheet.write(baris, 2, data_efaktur.invoice_id.partner_id.name , self.bold_with_border)
                worksheet.write(baris, 3, data_efaktur.name , self.bold_with_border)
                worksheet.write(baris, 4, data_efaktur.invoice_id.amount_untaxed , self.number_format)
                baris = baris + 1
                nomor = nomor + 1
            
        workbook.close()
        out=base64.encodestring(fp.getvalue())
        self.write({'state_x':'get', 'data_x':out, 'name': filename})

        ir_model_data = self.pool.get('ir.model.data')
        fp.close()
        form_res = ir_model_data.get_object_reference(self._cr, self._uid, 'pti_efaktur', 'efaktur_report_form')
        form_id = form_res and form_res[1] or False
        return {
            'name': _('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'efaktur.report',
            'res_id': self.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

