import logging
#import time
#from datetime import datetime
from dateutil import parser
#import uuid
#import sets

#from functools import partial

import openerp
import openerp.addons.decimal_precision as dp
from openerp import tools, models, SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools import float_is_zero
from openerp.tools.translate import _
from openerp.exceptions import UserError
import datetime


_logger = logging.getLogger(__name__)

#----------------------------------------------------------
# Products
#----------------------------------------------------------
class product_template(osv.osv):
    _inherit = "product.template"
    
    #ids false to get all ids product
    def inactive_product_expired(self, cr, uid, ids=False, context=None):
        all_product_list = self.pool.get('product.template')
        product_list_ids = all_product_list.search(cr, uid, [])
        all_list = all_product_list.browse(cr, uid,product_list_ids,context=context)
        for list_id in all_list:
            #if product is a voucher
            if (list_id.voucher==True):
                now = datetime.date.today()
                #if there is end_date
                if (list_id.end_date):
                    end_date_voucher = list_id.end_date
                    ending_date = datetime.datetime.strptime(end_date_voucher, '%Y-%m-%d').date()
                    #if today > end date product voucher do inactive product
                    if(now > ending_date):
                        print "Product Expired"
                        #set active : false
                        self.pool['product.template'].write(cr, uid, list_id.id, {'active': False,})
                    else:
                        print "Product Not Expired"
