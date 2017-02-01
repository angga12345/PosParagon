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
import base64
import xlwt
from xlwt import *
import cStringIO
import xlsxwriter
from cStringIO import StringIO
import tempfile
from openerp import models, fields, api, _
from openerp.exceptions import UserError
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger('GO-LIVE REPORT')
'''
select * from
    (select dc_id,count(id) as new_so,sum(amount_total) as new_credit  from sale_order 
        where create_date BETWEEN '2016-01-17' and '2016-01-18' group by dc_id) as SO 
    NATURAL JOIN 
    (select coalesce(journal.dc_id,(select id from res_partner where is_dc=True Limit 1)) as dc_id,sum(line.amount) as income from account_bank_statement_line line join account_journal journal on journal.id=line.journal_id 
        where line.create_date between '2016-01-17' and '2016-01-18' and line.amount>0 group by journal.dc_id) as INCOME
    NATURAL JOIN 
    (select journal.dc_id as dc_id,sum(line.amount) as outcome from account_bank_statement_line line join account_journal journal on journal.id=line.journal_id 
        where line.create_date between '2016-01-17' and '2016-01-18' and line.amount<0 group by journal.dc_id) as OUTCOME 
    NATURAL JOIN 
    (select loc.dc_id as dc_id,sum(mov.product_uom_qty) as total_arrived from stock_move mov JOIN stock_location loc ON mov.location_dest_id=loc.id 
        where mov.location_dest_id in (19, 28, 36, 44, 52, 60, 8049, 68, 76, 84, 92, 100, 108, 116, 124, 132, 140, 148, 156, 164, 172, 180, 188, 196, 204, 212, 220, 228, 236, 244, 8066) and mov.write_date BETWEEN '2016-01-17' and '2016-01-18' and mov.state='done' group by mov.location_dest_id,loc.dc_id) as ARRIVED 
    NATURAL JOIN 
    (select loc.dc_id as dc_id,sum(mv.product_uom_qty) as total_delivered from stock_move mv join stock_location loc ON loc.id=mv.location_id 
        where mv.location_id in (19, 28, 36, 44, 52, 60, 8049, 68, 76, 84, 92, 100, 108, 116, 124, 132, 140, 148, 156, 164, 172, 180, 188, 196, 204, 212, 220, 228, 236, 244, 8066) and mv.write_date BETWEEN '2016-01-17' and '2016-01-18' and mv.state='done' group by mv.location_id,loc.dc_id) AS DELIVERED
'''
class GoLive(models.TransientModel):
    
    _name = 'report.go.live'
    
    data_binary = fields.Binary(string='Go Live Report', help='Report Go Live')
    date_report = fields.Date(string='Date', domain="[('type','=','normal')]", required=0, select=1)
    state_position = fields.Selection([('choose','choose'),('get','get')],string='state',default='choose')
    name = fields.Char('Filename', readonly=True,default='must_have_go_live.xlsx')
    
    @api.multi
    def excel_report(self):
        return self._print_excel_report()
    
    def mergeData(self, temp, data):
        if not data:
            return temp
        
        def merge_two_dicts(x, y):
            '''Given two dicts, merge them into a new dict as a shallow copy.'''
            z = x.copy()
            z.update(y)
            return z
        
        res = []
        for t in temp:
            for s in data:
                if s['dc_id'] == t['dc_id']:
                    res.append(merge_two_dicts(t, s))
                    temp.remove(t)
                    temp.append(merge_two_dicts(t, s))
                    data.remove(s)
                    break
        return temp
    
    def prepareInformation(self, dates):
        results = []
        self.env.cr.execute("select id,name from res_partner where is_dc =True")
        dc_id = self.env.cr.fetchall()
        dc_datas = [[d[0],d[1]] for d in dc_id]
        dc_ids = [d[0] for d in dc_id]
        dc_datas = tuple(dc_datas)
        dc_ids = tuple(dc_ids)

        for id in dc_datas:
            results.append({'dc_id' : id[0], 'name' : id[1]})
        
        self.env.cr.execute("select id from stock_location where name ilike 'dc %'")
        dc_loc = self.env.cr.fetchall()
        loc_ids = [d[0] for d in dc_loc]
        loc_ids = tuple(loc_ids)
        
        _parsed = datetime.strptime(dates,"%Y-%m-%d")
        next_date = _parsed + timedelta(days=1)
        next_date = str(next_date.strftime('%Y-%m-%d'))
        dates = str(dates)
        sale_order = " select dc_id,count(id) as new_so,sum(amount_total) as new_credit "\
                   "         from sale_order "\
                   "        where "\
                   "        date_order BETWEEN '"+dates+"' and '"+next_date+"' group by dc_id;"
        self.env.cr.execute(sale_order)
        sale_result = self.env.cr.dictfetchall()
        results = self.mergeData(results, sale_result)
        
        cash_in = " select journal.dc_id,sum(line.amount) as income from account_bank_statement_line line join account_journal journal on journal.id=line.journal_id "\
                      " where line.create_date between '"+dates+"' and '"+next_date+"' and line.amount>0 group by journal.dc_id;"
        self.env.cr.execute(cash_in)
        income_result = self.env.cr.dictfetchall()
        results = self.mergeData(results, income_result)
        
        cash_out = " select journal.dc_id,sum(line.amount) as outcome from account_bank_statement_line line join account_journal journal on journal.id=line.journal_id "\
                      " where line.create_date between '"+dates+"' and '"+next_date+"' and line.amount<0 group by journal.dc_id;"
        self.env.cr.execute(cash_out)
        out_result = self.env.cr.dictfetchall()
        results = self.mergeData(results, out_result)
        
        arrived_to_dc = "select loc.dc_id,sum(mov.product_uom_qty) as total_arrived from stock_move mov JOIN stock_location loc ON mov.location_dest_id=loc.id "\
                        "where mov.location_dest_id in "+str(loc_ids)+" and "\
                        "mov.write_date BETWEEN '"+dates+"' and '"+next_date+"' and mov.state='done' group by mov.location_dest_id,loc.dc_id;"
        self.env.cr.execute(arrived_to_dc)
        arrived_result = self.env.cr.dictfetchall()
        results = self.mergeData(results, arrived_result)
        
        delivered = "select loc.dc_id,sum(mv.product_uom_qty) as total_delivered from stock_move mv join stock_location loc ON loc.id=mv.location_id "\
                    "where mv.location_id in "+str(loc_ids)+" and "\
                    "mv.write_date BETWEEN '"+dates+"' and '"+next_date+"' and mv.state='done' group by mv.location_id,loc.dc_id;"
        self.env.cr.execute(delivered)
        delivered_result = self.env.cr.dictfetchall()
        results = self.mergeData(results, delivered_result)

        return results
            
        
    def set_width(self, worksheet):
        worksheet.set_column('A1:A1', 4)
        worksheet.set_column('B1:B1', 20)
        worksheet.set_column('C1:C1', 4)
        worksheet.set_column('D1:F1', 20)
        worksheet.set_column('G1:G1', 12)
        worksheet.set_column('H1:H1', 15)
        
        return worksheet
                
    def _print_excel_report(self):
        fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)
        bold_left_number = workbook.add_format({'align': 'right','num_format': '#,##0.0'})
        bold_left_number.set_border()
	border = workbook.add_format({})
	border.set_border()
        
        date = self.date_report
        self.prepareInformation(date)
        worksheet = workbook.add_worksheet("Go-Live report")
        worksheet = self.set_width(worksheet)
        worksheet.write(0, 0, "Go-Live report", bold_left_number)
        worksheet.write(1, 0, date, bold_left_number)
        
        worksheet.write(3, 0, "No.", bold_left_number)
        worksheet.write(3, 1, "Name", bold_left_number)
        worksheet.merge_range('C4:D4', "Sales" , bold_left_number)
        worksheet.write(3, 4, "Cash/Bank in", bold_left_number)
        worksheet.write(3, 5, "Cash/Bank out", bold_left_number)
        worksheet.write(3, 6, "Stock items in", bold_left_number)
        worksheet.write(3, 7, "Stock items out", bold_left_number)

        baris = 4
        datas_to_show = self.prepareInformation(date)
        print datas_to_show
        print len(datas_to_show)
        numb = 1
        for column in datas_to_show:
            col_idx = 0
            worksheet.write(baris, col_idx, numb, border);col_idx+=1
            worksheet.write(baris, col_idx, column['name'] if column.has_key('name') else '', border);col_idx+=1
            worksheet.write(baris, col_idx, column['new_so'] if column.has_key('new_so') else 0, bold_left_number);col_idx+=1
            worksheet.write(baris, col_idx, column['new_credit'] if column.has_key('new_credit') else 0, bold_left_number);col_idx+=1
            worksheet.write(baris, col_idx, column['income']  if column.has_key('income') else 0, bold_left_number);col_idx+=1
            worksheet.write(baris, col_idx, column['outcome'] if column.has_key('outcome') else 0, bold_left_number);col_idx+=1
            worksheet.write(baris, col_idx, column['total_arrived'] if column.has_key('total_arrived') else 0, bold_left_number);col_idx+=1
            worksheet.write(baris, col_idx, column['total_delivered'] if column.has_key('total_delivered') else 0, bold_left_number);col_idx+=1
            baris += 1
            numb += 1
        
        workbook.close()

        out=base64.encodestring(fp.getvalue())
        self.update({'state_position':'get', 'data_binary':out, 'name': self.name})
        _logger.info ("===REPORT READY TO SERVE===")

        ir_model_data = self.pool.get('ir.model.data')
        fp.close()

        form_res = ir_model_data.get_object_reference(self._cr, self._uid, 'pti_invoice_report', 'report_go_live_view')
        form_id = form_res and form_res[1] or False
        return {
            'name': _('Download XLS'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'report.go.live',
            'res_id': self.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    

