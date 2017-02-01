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

#-*- coding:utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import SUPERUSER_ID
from openerp import models, fields, api, _
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.tools.amount_to_text_en import amount_to_text
from datetime import datetime

import time

import logging
from openerp.exceptions import UserError
_log = logging.getLogger(__name__)


class pti_do_report(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        res = super(pti_do_report, self).__init__(cr, SUPERUSER_ID, name, context)
        self.localcontext.update({
            'set_notify': self._set_notify,
            'set_term_delivery': self._term_delivery,
        })
            
    
    def _set_notify(self, obj):
        do_id = obj.id
        notif_true = True
        cr = self.cr
        cr.execute('update stock_picking set notif_report_printed=%s '\
            'where id=%s', ('True', do_id))

        _log.info ("Ubah notif report printing di stock.picking ")
        return True
    
    def _term_delivery(self, obj):
        do_id = obj.id

        term = datetime.strptime(obj.min_date, "%Y-%m-%d %H:%M:%S") #type datetime
        time_do_create = datetime.strptime(obj.date_create_do, "%Y-%m-%d %H:%M:%S") #type datetime
        term_of_delivery = term - time_do_create
        
        obj.term_of_delivery_time = str(term_of_delivery) #change from datetime to string
        
        return term_of_delivery           
    
class report_pti_do_report(osv.AbstractModel):
    _name = 'report.pti_do_report.report_delivery_note'
    _inherit = 'report.abstract_report'
    _template = 'pti_do_report.report_delivery_note'
    _wrapped_report_class = pti_do_report

##############boolean printed for delivery sort####################
class report_pti_do_report_sort(osv.AbstractModel):
    _name = 'report.pti_do_report.report_delivery_note_sorted'
    _inherit = 'report.abstract_report'
    _template = 'pti_do_report.report_delivery_note_sorted'
    _wrapped_report_class = pti_do_report

##############boolean printed for delivery letter####################
class report_pti_do_report_letter(osv.AbstractModel):
    _name = 'report.pti_do_report.report_delivery_note_letter'
    _inherit = 'report.abstract_report'
    _template = 'pti_do_report.report_delivery_note_letter'
    _wrapped_report_class = pti_do_report
    
class pti_do_report_proforma(report_sxw.rml_parse):
     
    def __init__(self, cr, uid, name, context):
        super(pti_do_report_proforma, self).__init__(cr, SUPERUSER_ID, name, context)
        self.localcontext.update({
            'set_notify': self._set_notify,
            'get_lines': self._get_lines,
            'get_order_subtotal': self._get_order_subtotal,
            'get_order_disc_volume': self._get_order_disc_volume,
            'get_order_disc_add': self._get_order_disc_add,
            'get_order_disc_program': self._get_order_disc_program,
            'get_order_disc_global': self._get_order_disc_global,
            'get_order_disc_global_val': self._get_order_disc_global_val,
            'get_order_net': self._get_order_net,
            'get_order_tot_disc' : self._get_order_tot_disc,
            'get_order_tax': self._get_order_tax,
            'get_order_total': self._get_order_total,
            'get_order_total_text': self._get_order_total_text,
        })
        self.order_subtotal = 0
        self.order_disc_volume = 0
        self.order_disc_add = 0
        self.order_disc_program = 0
        self.order_distr_fee = 0
        self.order_freight = 0
        self.order_tax = 0
        self.order_disc_global = []
        self.order_disc_global_val = 0
             
    def _set_notify(self, obj):
        do_id = obj.id
        notif_true = True
        cr = self.cr
        cr.execute('update stock_picking set proforma_printed=%s '\
            'where id=%s', ('True', do_id))         
        return True
             
    def _get_order_subtotal(self):
        return self.order_subtotal
             
    def _get_order_disc_volume(self):
        return self.order_disc_volume
             
    def _get_order_disc_add(self):
        return self.order_disc_add
             
    def _get_order_disc_program(self):
        return self.order_disc_program
             
    def _get_order_disc_global(self):
        return self.order_disc_global
        
    def _get_order_disc_global_val(self):
        return self.order_disc_global_val
        
    def _get_order_tax(self):
        return self.order_tax
        
    def _get_order_net(self):
        net = self._get_order_subtotal()-self._get_order_disc_volume()-self._get_order_disc_add()-self._get_order_disc_program()-self._get_order_disc_global_val()
        return net
        
    def _get_order_tot_disc(self):
        tot_disc = self._get_order_disc_volume()+self._get_order_disc_add()+self._get_order_disc_program()+self._get_order_disc_global_val()
        return tot_disc
        
    def _get_order_total(self):
        total = self._get_order_net()+self._get_order_tax()
        return total
        
    def _get_order_total_text(self):
        return amount_to_text(self._get_order_total(), 'en', '')
        
    def _get_lines(self, obj):
        do_id = obj.id
        lines = []
        self.order_subtotal = 0
        self.order_disc_volume = 0
        self.order_disc_add = 0
        self.order_disc_program = 0
        self.order_tax = 0
        self.order_distr_fee = 0
        self.order_freight = 0
        self.order_disc_global = []
        self.order_disc_global_val = 0
        price_subtotal_before_global = 0
        for line in obj.move_lines:
            product_code = line.product_id.default_code or ''
            product_name = line.product_id.name
            sale_line = line.procurement_id and line.procurement_id.sale_line_id and line.procurement_id.sale_line_id or False
            price_unit = sale_line and sale_line.price_unit or 0
            product_qty = line.product_uom_qty
            product_uom = line.product_id.uom_id.name
            price_subtotal = 0
            tot_disc_volume = 0
            tot_disc_add = 0
            tot_disc_program = 0
            tot_disc_global = 0
            state = line.state
            total_before_disc = price_unit*product_qty
            subtotal = total_before_disc
            tot_disc_volume, tot_disc_add,\
            tot_disc_program, subtotal, disc_global = self.get_discounts(sale_line,\
                                                                   subtotal,\
                                                                   tot_disc_volume,\
                                                                   tot_disc_add,\
                                                                   tot_disc_program)
            price_subtotal = subtotal #pricesubtotal before global disc - per line
            price_subtotal_before_global = price_subtotal
            tot_disc_global = 0
            order_disc_global = self.order_disc_global
            subtotal, tot_disc_global = self.getdiscountGlobal(order_disc_global, subtotal, disc_global)

            tax_line = 0
            if sale_line:
                taxes = sale_line.tax_id.compute_all(subtotal, sale_line.order_id.currency_id, 1, 
                                                product=sale_line.product_id, partner=sale_line.order_id.partner_id)
                tax_line = taxes['total_included'] - taxes['total_excluded']
            
            self.order_subtotal+=total_before_disc
            self.order_disc_volume += tot_disc_volume
            self.order_disc_add += tot_disc_add
            self.order_disc_program += tot_disc_program
            self.order_disc_global_val += tot_disc_global
            self.order_tax += tax_line
                
            lines.append({
                'state':state,
                'product_code':product_code,
                'is_free' : False,
                'product_name':product_name,
                'price_unit':price_unit,
                'product_qty':product_qty,
                'product_uom':product_uom,
                'tot_disc_volume':tot_disc_volume,
                'tot_disc_add':tot_disc_add,
                'tot_disc_program':tot_disc_program,
                'price_subtotal':price_subtotal,
            })
            #add free product
            total_free = 0
            if sale_line:
                sol_obj = self.pool.get('sale.order.line')
                free_line_ids = sol_obj.search(self.cr, self.uid,[('is_free','=',True),('order_id','=', sale_line.order_id.id),('product_id','=',sale_line.product_id.id)])
                if free_line_ids:
                    free_sol = sol_obj.browse(self.cr, self.uid, free_line_ids[0])
                    tot_disc_volume = 0
                    tot_disc_add = 0
                    tot_disc_program = 0
                    subtotal = total_before_disc = free_sol.price_unit * free_sol.product_uom_qty * -1
                    tot_disc_volume, tot_disc_add,\
                    tot_disc_program, subtotal, disc_global = self.get_discounts(free_sol, \
                                                                                 total_before_disc, \
                                                                                 tot_disc_volume, \
                                                                                 tot_disc_add, \
                                                                                 tot_disc_program)
                    subtotal_before_global = subtotal
                    subtotal, tot_disc_global = self.getdiscountGlobal(order_disc_global, subtotal, disc_global)
                    lines.append({
                        'state':state,
                        'product_code':product_code,
                        'is_free' : True,
                        'product_name':free_sol.name,
                        'price_unit':free_sol.price_unit,
                        'product_qty':free_sol.product_uom_qty,
                        'product_uom':free_sol.product_uom.name,
                        'tot_disc_volume':tot_disc_volume,
                        'tot_disc_add':tot_disc_add,
                        'tot_disc_program':tot_disc_program,
                        'price_subtotal':subtotal_before_global,
                    })
                    self.order_subtotal+=total_before_disc
                    self.order_disc_volume += tot_disc_volume
                    self.order_disc_add += tot_disc_add
                    self.order_disc_program += tot_disc_program
                    self.order_disc_global_val += tot_disc_global
                    total_free+=free_sol.price_subtotal * -1
                    # free_sol.price_tax is negatif
                    tax_line = 0
                    if free_sol:
                        taxes = free_sol.tax_id.compute_all(subtotal*-1, free_sol.order_id.currency_id, 1, 
                                                        product=free_sol.product_id, partner=free_sol.order_id.partner_id)
                        tax_line = taxes['total_included'] - taxes['total_excluded']
                    self.order_tax += tax_line * -1

        subtotal = price_subtotal_before_global
        lines = sorted(lines, key=lambda k: [k['product_code'], k['is_free']]) 
        return lines
    
    def get_discounts(self, line, subtotal, tot_disc_volume, tot_disc_add, tot_disc_program):
        disc_volume = []
        disc_add= []
        disc_program= []
        disc_global= []
        if line:
            for disc in line.discount_m2m:
                if disc.type == 'volume':
                    disc_volume.append(disc.percentage)
                elif disc.type == 'additional':
                    disc_add.append(disc.percentage)
                elif disc.type == 'extra':
                    disc_program.append(disc.percentage)
                elif disc.type == 'sale_order':
                    disc_global.append(disc)

        for disc in disc_volume:
            disc_value = subtotal*disc/100.0
            subtotal = subtotal - disc_value
            tot_disc_volume+=disc_value
        for disc in disc_add:
            disc_value = subtotal*disc/100.0
            subtotal = subtotal - disc_value
            tot_disc_add+=disc_value
        for disc in disc_program:
            disc_value = subtotal*disc/100.0
            subtotal = subtotal - disc_value
            tot_disc_program+=disc_value
        return tot_disc_volume, tot_disc_add, tot_disc_program, subtotal, disc_global
    
    def getdiscountGlobal(self, order_disc_global, subtotal, disc_global):
        tot_disc_global = 0
        for disc in disc_global:
            name_disc = disc.name
            disc_value = subtotal*disc.percentage/100.0
            subtotal = subtotal - disc_value
            tot_disc_global += disc_value
            res = filter(lambda order_disc_global: order_disc_global['id_disc'] == disc.id, order_disc_global)
            if res:
                total = res[0]['discount_value'] + disc_value
                for d in order_disc_global:
                    d.update(('discount_value', total) for k, v in d.iteritems() if v == disc.id and k=='id_disc')
            else:
                self.order_disc_global.append({'discount_value' : disc_value,
                                               'name_discount' : name_disc,
                                               'id_disc':disc.id})
                self.order_disc_global = order_disc_global
        return subtotal, tot_disc_global
class report_pti_do_report_proforma(osv.AbstractModel):
    _name = 'report.pti_do_report.report_pi'
    _inherit = 'report.abstract_report'
    _template = 'pti_do_report.report_pi'
    _wrapped_report_class = pti_do_report_proforma

# class stock_picking_operation(report_sxw.rml_parse):
#      
#     def __init__(self, cr, uid, name, context):
#         super(stock_picking_operation, self).__init__(cr, SUPERUSER_ID, name, context)
#         self.localcontext.update({
#             'set_notify': self._set_notify,
#         })
#              
#      
#     def _set_notify(self, obj):
#         do_id = obj.id
#         notif_true = True
#         cr = self.cr
#         cr.execute('update stock_picking set notif_report_printed=%s '\
#             'where id=%s', ('True', do_id))         
#         return True
#      
# class report_stock_picking_operation(osv.AbstractModel):
#     _name = 'report.stock.report_picking'
#     _inherit = 'report.abstract_report'
#     _template = 'stock.report_picking'
#     _wrapped_report_class = stock_picking_operation    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:= pti_do_report_proforma
    
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

