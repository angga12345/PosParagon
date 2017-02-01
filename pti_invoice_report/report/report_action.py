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
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.tools.amount_to_text_en import amount_to_text

import time

import logging
_log = logging.getLogger(__name__)


class pti_invoice_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(pti_invoice_report, self).__init__(cr, SUPERUSER_ID, name, context)
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
            'get_sale_order' : self._get_sale_order,
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

    def _get_sale_order(self, obj):
        sale_info = []
        print obj.invoice_line_ids
        if obj.invoice_line_ids:
            i = 1
            for invoice_line in obj.invoice_line_ids:
                if i==1:
                    for so in invoice_line.sale_line_ids:
                        sale_info.append({'sale_order' : so.order_id.name,
                                          'customer_po' : so.order_id.client_order_ref,
                                          })
                        break
                    break
        print sale_info
        return sale_info
    
    def _get_customer_po(self):
        return self.customer_po
    
    def _set_notify(self, obj):
        do_id = obj.id
        notif_true = True
        cr = self.cr
        cr.execute('update stock_picking set notif_report_printed=%s '
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
        self.order_tax = obj.amount_tax
        self.order_distr_fee = 0
        self.order_freight = 0
        self.order_disc_global = []
        self.order_disc_global_val = 0
        price_subtotal_before_global = 0
        for line in obj.invoice_line_ids:
            product_code = line.product_id.default_code or ''
            product_name = line.product_id.name
            product_qty = line.quantity
            product_uom = line.uom_id.name
            price_unit = line and line.price_unit or 0
            price_subtotal = 0
            tot_disc_volume = 0
            tot_disc_add = 0
            tot_disc_program = 0
            tot_disc_global = 0

            disc_volume = []
            disc_add = []
            disc_program = []
            disc_global = []

            for disc in line.discount_m2m:
                if disc.type == 'volume':
                    disc_volume.append(disc.percentage)
                elif disc.type == 'additional':
                    disc_add.append(disc.percentage)
                elif disc.type == 'extra':
                    disc_program.append(disc.percentage)
                elif disc.type == 'sale_order':
                    disc_global.append(disc)

            total_before_disc = price_unit*product_qty
            subtotal = total_before_disc
            for disc in disc_volume:
                disc_value = subtotal*disc/100.0
                subtotal = subtotal - disc_value
                tot_disc_volume += disc_value
                
            for disc in disc_add:
                disc_value = subtotal*disc/100.0
                subtotal = subtotal - disc_value
                tot_disc_add += disc_value
                
            for disc in disc_program:
                disc_value = subtotal*disc/100.0
                subtotal = subtotal - disc_value
                tot_disc_program += disc_value
                
            # price subtotal before global disc - per line
            price_subtotal = subtotal
            price_subtotal_before_global = price_subtotal
            tot_disc_global = 0
            order_disc_global = self.order_disc_global
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

            self.order_subtotal += total_before_disc
            self.order_disc_volume += tot_disc_volume
            self.order_disc_add += tot_disc_add
            self.order_disc_program += tot_disc_program
            self.order_disc_global_val += tot_disc_global

            lines.append({
                'product_code': product_code,
                'is_free' : line.is_free,
                'product_name':line.name,
                'price_unit': price_unit,
                'product_qty': product_qty,
                'product_uom': product_uom,
                'tot_disc_volume': tot_disc_volume,
                'tot_disc_add': tot_disc_add,
                'tot_disc_program': tot_disc_program,
                'price_subtotal': price_subtotal,
            })
        subtotal = price_subtotal_before_global
        lines = sorted(lines, key=lambda k: [k['product_code'], k['is_free']]) 
        return lines


class report_pti_invoice_report(osv.AbstractModel):
    _name = 'report.pti_invoice_report.report_inv'
    _inherit = 'report.abstract_report'
    _template = 'pti_invoice_report.report_inv'
    _wrapped_report_class = pti_invoice_report


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:= pti_invoice_report
    
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

