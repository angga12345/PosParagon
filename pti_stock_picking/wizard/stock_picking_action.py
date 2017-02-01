from openerp.osv import fields, osv
from openerp import models, fields, api, _
from openerp.exceptions import UserError
import logging
_log = logging.getLogger(__name__)

class mark_as_todo(models.TransientModel):
    _name = 'stock.picking.action'

    @api.multi
    def action_confirm(self):
        pickings = self.env.context.get('active_ids')
        stock_pickings = self.env['stock.picking'].browse(pickings)
        for picking in stock_pickings:
            picking.action_confirm()
            
    @api.multi
    def action_assign(self):
        pickings = self.env.context.get('active_ids')
        stock_pickings = self.env['stock.picking'].browse(pickings)    
        for picking in stock_pickings:
            picking.action_assign()
            
    @api.multi
    def process_set_all(self):
        pickings = self.env.context.get('active_ids')
        stock_pickings = self.env['stock.picking'].browse(pickings)
        for picking1 in stock_pickings:
            if  picking1.state == 'draft' or all([x.qty_done == 0.0 for x in picking1.pack_operation_ids]):
                if picking1.state == 'draft':
                    picking1.action_confirm()
                    if picking1.state != 'assigned':
                        picking1.action_assign()
                        if picking1.state != 'assigned':
                            raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
                for pack in picking1.pack_operation_ids:
                    if pack.product_qty > 0:
                        pack.write({'qty_done': pack.product_qty})
                    else:
                        pack.unlink()
                picking1.do_transfer()
            else:
                picking1.do_new_transfer()
    
    """
    action validate in all transfer
    extend function in button validate form, make some adjustment
    """
    @api.multi
    def do_new_transfer(self):
        pickings = self.env.context.get('active_ids')
        stock_pickings = self.env['stock.picking'].browse(pickings)
        vals=False
        """checking if there is picking not set all done"""
        for picking_bol in stock_pickings:
            if  all([x.qty_done == 0.0 for x in picking_bol.pack_operation_ids]):
                vals=True
        if vals==True:
            context={}
            context.update({'active_ids':pickings})
            view_id = self.env.ref('pti_stock_picking.view_validate_transfer',False)
            return {
                'name':_("Set All Done?"),
                'view_mode': 'form',
                'res_id':self.id,
                'view_id': view_id.id,
                'views': [(view_id.id, 'form')],
                'view_type': 'form',
                'res_model': 'stock.picking.action',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context':context
                }   
        else:
            for picking in stock_pickings:
                picking.do_new_transfer()