'''
Created on Dec 5, 2016

@author: nurina
'''
from openerp import models, fields, api
from openerp.tools.translate import _

class CustomerValidation(models.TransientModel):
    """
    Customer Validation wizard
    """
    _name = 'partner.customer.validation'
    _description = 'Customer Validation'
    
    @api.multi
    def get_validate(self):
        ac_move_ids = self._context.get('active_ids', False)
    
        res = self.env['res.partner'].browse(ac_move_ids).customer_active()
        if res:
            return {
                'name': _('Customer Validation'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'res.partner',
                'domain': [('id', 'in', res)],
            }
        return {'type': 'ir.actions.act_window_close'}

    