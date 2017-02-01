import logging
import uuid
import sets

from functools import partial

import openerp
import openerp.addons.decimal_precision as dp
import time
from datetime import datetime
from openerp import models, SUPERUSER_ID, fields, api, _
from openerp.tools import float_is_zero
from openerp.tools.translate import _
from openerp.exceptions import UserError
#from pygments.lexer import _inherit

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"
    
    @api.multi
    def assert_balanced(self):
        if not self.ids:
            return True
        prec = self.env['decimal.precision'].precision_get('Account')

        self._cr.execute("""\
            SELECT      move_id
            FROM        account_move_line
            WHERE       move_id in %s
            GROUP BY    move_id
            HAVING      abs(sum(debit) - sum(credit)) > %s
            """, (tuple(self.ids), 10 ** (-max(5, prec))))
        #print "DAAAAAAAAAAAAAAA",self._cr.fetchall()

        if len(self._cr.fetchall()) != 0:
            raise UserError(_("Cannot create unbalanced journal entry."))
        return True

#membership type
class member_types(models.Model):
    _name = "member.types"
    
    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    percentage = fields.Float('Percentage')
    expired_date = fields.Date(string='Expired Date')


# res partner : partner
class partner(models.Model):
    _inherit = "res.partner"
    
    is_pos_membership = fields.Boolean("Member Of POS")
    ID_card_number = fields.Char("ID Card Number")
    university = fields.Char("University")
    community = fields.Char("Community")
    
    @api.one
    @api.onchange('is_pos_membership')
    def onchange_pos_membership(self):        
        obj_silver = self.env['member.types'].search([('code', '=',"1")])
        obj_bol=True
        Obj_member=self.is_pos_membership
        if Obj_member == obj_bol:
#             print "---------true option-------------"
            self.discount_member_id=obj_silver
        else:
            self.discount_member_id=""
    
    @api.model
    def _get_defaultSilver(self):
        silver = self.env['member.types'].search([('code','=',1)])
        print "member name :",silver.name
        print "member id :",silver.id
        return silver
    
    
    discount_member_id = fields.Many2one('member.types','Membership Discount')
    disc_percentage = fields.Float(related = 'discount_member_id.percentage', string='Percentage', store=True)
