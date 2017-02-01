import json
from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp import api, fields, models, _
from openerp.tools import float_is_zero
from openerp.tools.misc import formatLang

from openerp.exceptions import UserError, RedirectWarning, ValidationError

import openerp.addons.decimal_precision as dp

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def invoice_line_move_line_get(self):
        res = super(AccountInvoice, self).invoice_line_move_line_get()
        new_res = []
        if self.type in ('out_invoice','out_refund'):
            
            for free in self.invoice_line_ids:
                if free.is_free is True:
                    res_comp = self.env['res.company'].search([])
                    for acc_free in res_comp:
                        if acc_free.account_id.id is False :
                            raise UserError(_("Please fill account for free products on setting Accounting."))
                        else:
                            account_free_id = acc_free.account_id.id
                    free.account_id = account_free_id
                else :
                    free.account_id = free.account_id
                
                pr = free.price_unit * free.quantity
                fr = {
                      'account_id' :free.account_id.id,
                      'price':pr,
                      'name': free.name,
                      'dc_id' : self.dc_id.id,
                      'invoice_id': self.id
                      }
                new_res.append(fr)
            new_res += self.discount_line_move_line_get()
            
        else:
            materials = []
            for x in res:
                res = filter(lambda materials: materials['account_id'] == x['account_id'], materials)
                if res:
                    total = res[0]['price'] + x['price']
                    for d in materials:
                        d.update(('price', total) for k, v in d.iteritems() if
                                 v == x['account_id'] and k == 'account_id')
                else:
                    ''' if not exist in materials create new '''
                    move_line_dict = {
                        'invl_id': x.get('invl_id'),
                        'type': 'src',
                        'name': x.get('name'),
                        'price_unit': 0.0,
                        'quantity': x.get('quantity'),
                        'price': x.get('price'),
                        'account_id': x.get('account_id'),
                        'product_id': x.get('product_id'),
                        'uom_id': x.get('uom_id'),
                        'account_analytic_id': x.get('account_analytic_id'),
                        'tax_ids': x.get('tax_ids'),
                        'invoice_id': self.id,
                    }
                    materials.append(move_line_dict)
            new_res = materials
        return new_res

    @api.model
    def discount_line_move_line_get(self):
        '''
        price negative will register to debit
        '''
        amlines = []

         
        for invoice_line in self.invoice_line_ids:
            disc_1= []
            disc_2= []
            disc_3= []
            disc_4= []
            disc_5= []
            disc_6= []
            
            for discount in invoice_line.discount_m2m:
                if discount.sequence_discount is False or discount.account_id is False:
                    raise UserError(_("Please fill Account or sequence for discount before validate."))
                elif discount.sequence_discount == '1':
                    disc_1.append(discount)
                elif discount.sequence_discount == '2':
                    disc_2.append(discount)
                elif discount.sequence_discount == '3':
                    disc_3.append(discount)
                elif discount.sequence_discount == '4':
                    disc_4.append(discount)
                elif discount.sequence_discount == '5':
                    disc_5.append(discount)
                elif discount.sequence_discount == '6':
                    disc_6.append(discount)

            price_unit = abs(invoice_line.price_unit) 
            for disc in disc_1:
                is_free = invoice_line.is_free
                price_temp = price_unit * (1 - (disc.percentage or 0.0) / 100.0)
                discount_amount = price_unit - price_temp
                price_unit = price_temp
                price = discount_amount * invoice_line.quantity
                 
                account_obj = self.env['account.account'].search([('name','=',disc.account_id.name)],limit = 1)
                res = filter(lambda amlines: amlines['account_id'] == account_obj.id \
                             and amlines['is_free'] == is_free, amlines)
                if res:
                    if not is_free:
                        price = price * -1
                         
                    for d in amlines:
                        for k, v in d.iteritems():
                            if d['is_free'] == True :
                                total = res[0]['price'] + price
                                if (v == account_obj.id and k=='account_id') :
                                    d.update(('price', total) for k, v in d.iteritems() if (v== is_free and k=='is_free'))
                                else :
                                    next
                                     
                            if d['is_free'] == False :
                                total = res[0]['price'] + price
                                if (v == account_obj.id and k=='account_id') :
                                    d.update(('price', total) for k, v in d.iteritems() if (v== is_free and k=='is_free'))
                                else :
                                    next                            
 
                else:
                    ''' if not exist in amlines create new '''
                    if not is_free:
                        price = price * -1
                    vals = {'price' : price,
                            'name': disc.account_id.name,
                            'account_id': account_obj.id,
                            'dc_id' : invoice_line.invoice_id.dc_id.id,
                            'is_free' : is_free,
                            }
                    amlines.append(vals)
 
 
            for disc in disc_2:
                is_free = invoice_line.is_free
                price_temp = price_unit * (1 - (disc.percentage or 0.0) / 100.0)
                discount_amount = price_unit - price_temp
                price_unit = price_temp
                price = discount_amount * invoice_line.quantity
                 
                account_obj = self.env['account.account'].search([('name','=',disc.account_id.name)],limit = 1)
                res = filter(lambda amlines: amlines['account_id'] == account_obj.id \
                             and amlines['is_free'] == is_free, amlines)
                if res:
                    if not is_free:
                        price = price * -1
                         
                    for d in amlines:
                        for k, v in d.iteritems():
                            if res[0]['is_free'] == True :
                                total = res[0]['price'] + price
                                if (v == account_obj.id and k=='account_id') :
                                    d.update(('price', total) for k, v in d.iteritems() if (v== is_free and k=='is_free'))
                                else :
                                    next
                            if res[0]['is_free'] == False :
                                total = res[0]['price'] + price
                                if (v == account_obj.id and k=='account_id') :
                                    d.update(('price', total) for k, v in d.iteritems() if (v== is_free and k=='is_free'))
                                else :
                                    next                            
 
                else:
                    ''' if not exist in amlines create new '''
                    if not is_free:
                        price = price * -1
                    vals = {'price' : price,
                            'name': disc.account_id.name,
                            'account_id': account_obj.id,
                            'dc_id' : invoice_line.invoice_id.dc_id.id,
                            'is_free' : is_free,
                            }
                    amlines.append(vals)
 
            for disc in disc_3:
                is_free = invoice_line.is_free
                price_temp = price_unit * (1 - (disc.percentage or 0.0) / 100.0)
                discount_amount = price_unit - price_temp
                price_unit = price_temp
                price = discount_amount * invoice_line.quantity
 
                account_obj = self.env['account.account'].search([('name','=',disc.account_id.name)],limit = 1) 
                res = filter(lambda amlines: amlines['account_id'] == account_obj.id \
                             and amlines['is_free'] == is_free, amlines)
                if res:
                    if not is_free:
                        price = price * -1
                         
                    for d in amlines:
                        for k, v in d.iteritems():
                            if res[0]['is_free'] == True :
                                total = res[0]['price'] + price
                                if (v == account_obj.id and k=='account_id') :
                                    d.update(('price', total) for k, v in d.iteritems() if (v== is_free and k=='is_free'))
                                else :
                                    next
                            if res[0]['is_free'] == False :
                                total = res[0]['price'] + price
                                if (v == account_obj.id and k=='account_id') :
                                    d.update(('price', total) for k, v in d.iteritems() if (v== is_free and k=='is_free'))
                                else :
                                    next                            
 
                else:
                    ''' if not exist in amlines create new '''
                    if not is_free:
                        price = price * -1
                    vals = {'price' : price,
                            'name': disc.account_id.name,
                            'account_id': account_obj.id,
                            'dc_id' : invoice_line.invoice_id.dc_id.id,
                            'is_free' : is_free,
                            }
                    amlines.append(vals)
                         
            for disc in disc_4:
                is_free = invoice_line.is_free
                price_temp = price_unit * (1 - (disc.percentage or 0.0) / 100.0)
                discount_amount = price_unit - price_temp
                price_unit = price_temp
                price = discount_amount * invoice_line.quantity
 
                account_obj = self.env['account.account'].search([('name','=',disc.account_id.name)],limit = 1)
                res = filter(lambda amlines: amlines['account_id'] == account_obj.id \
                             and amlines['is_free'] == is_free, amlines)
                 
                if res:
                    if not is_free:
                        price = price * -1
                         
                    for d in amlines:
                        for k, v in d.iteritems():
                            if res[0]['is_free'] == True :
                                total = res[0]['price'] + price
                                if (v == account_obj.id and k=='account_id') :
                                    d.update(('price', total) for k, v in d.iteritems() if (v== is_free and k=='is_free'))
                                else :
                                    next
                            if res[0]['is_free'] == False :
                                total = res[0]['price'] + price
                                if (v == account_obj.id and k=='account_id') :
                                    d.update(('price', total) for k, v in d.iteritems() if (v== is_free and k=='is_free'))
                                else :
                                    next                            
 
                else:
                    ''' if not exist in amlines create new '''
                    if not is_free:
                        price = price * -1
                    vals = {'price' : price,
                            'name': disc.account_id.name,
                            'account_id': account_obj.id,
                            'dc_id' : invoice_line.invoice_id.dc_id.id,
                            'is_free' : is_free,
                            }
                    amlines.append(vals)
                        
            for disc in disc_5:
                is_free = invoice_line.is_free
                price_temp = price_unit * (1 - (disc.percentage or 0.0) / 100.0)
                discount_amount = price_unit - price_temp
                price_unit = price_temp
                price = discount_amount * invoice_line.quantity
 
                account_obj = self.env['account.account'].search([('name','=',disc.account_id.name)],limit = 1)
                res = filter(lambda amlines: amlines['account_id'] == account_obj.id \
                             and amlines['is_free'] == is_free, amlines)
                 
                if res:
                    if not is_free:
                        price = price * -1
                         
                    for d in amlines:
                        for k, v in d.iteritems():
                            if res[0]['is_free'] == True :
                                total = res[0]['price'] + price
                                if (v == account_obj.id and k=='account_id') :
                                    d.update(('price', total) for k, v in d.iteritems() if (v== is_free and k=='is_free'))
                                else :
                                    next
                            if res[0]['is_free'] == False :
                                total = res[0]['price'] + price
                                if (v == account_obj.id and k=='account_id') :
                                    d.update(('price', total) for k, v in d.iteritems() if (v== is_free and k=='is_free'))
                                else :
                                    next                            
 
                else:
                    ''' if not exist in amlines create new '''
                    if not is_free:
                        price = price * -1
                    vals = {'price' : price,
                            'name': disc.account_id.name,
                            'account_id': account_obj.id,
                            'dc_id' : invoice_line.invoice_id.dc_id.id,
                            'is_free' : is_free,
                            }
                    amlines.append(vals)
                        
            for disc in disc_6:
                is_free = invoice_line.is_free
                price_temp = price_unit * (1 - (disc.percentage or 0.0) / 100.0)
                discount_amount = price_unit - price_temp
                price_unit = price_temp
                price = discount_amount * invoice_line.quantity
 
                account_obj = self.env['account.account'].search([('name','=',disc.account_id.name)],limit = 1)
                res = filter(lambda amlines: amlines['account_id'] == account_obj.id \
                             and amlines['is_free'] == is_free, amlines)
                 
                if res:
                    if not is_free:
                        price = price * -1
                         
                    for d in amlines:
                        for k, v in d.iteritems():
                            if res[0]['is_free'] == True :
                                total = res[0]['price'] + price
                                if (v == account_obj.id and k=='account_id') :
                                    d.update(('price', total) for k, v in d.iteritems() if (v== is_free and k=='is_free'))
                                else :
                                    next
                            if res[0]['is_free'] == False :
                                total = res[0]['price'] + price
                                if (v == account_obj.id and k=='account_id') :
                                    d.update(('price', total) for k, v in d.iteritems() if (v== is_free and k=='is_free'))
                                else :
                                    next                            
 
                else:
                    ''' if not exist in amlines create new '''
                    if not is_free:
                        price = price * -1
                    vals = {'price' : price,
                            'name': disc.account_id.name,
                            'account_id': account_obj.id,
                            'dc_id' : invoice_line.invoice_id.dc_id.id,
                            'is_free' : is_free,
                            }
                    amlines.append(vals)
        return amlines
    
    @api.model
    def line_get_convert(self, line, part):
        account_move_line_value = super(AccountInvoice, self).line_get_convert(line, part)
        account_move_line_value['dc_id'] = line.get('dc_id', False)
        return account_move_line_value
