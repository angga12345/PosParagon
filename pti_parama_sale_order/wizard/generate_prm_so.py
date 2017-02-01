from openerp import fields, models, api, _
from openerp.exceptions import except_orm
import datetime
import time

class generate_prm_so(models.TransientModel):
    _name = "generate.prm.so"
    
    
    @api.multi
    def generate_prm(self):
        lines = []
        partner_obj = self.env['res.partner'].search([('name','=','Parama')])
        warehouse_obj = self.env['stock.warehouse'].search([('name','=','Paragon:Parama')])
        now = datetime.datetime.now() - datetime.timedelta(days=1)
        date = now.strftime("%Y-%m-%d")
        invoice_id = self.env['account.invoice'].search([('number','like','PRM/'),
                                                         ('state_merge','in',('open','paid','refund')),
                                                         ('parama_so_id','=',False),
                                                         ('date_posted','<=',date)])

        if invoice_id:
            ir_model_data = self.env['ir.model.data']
            order_method_id = ir_model_data.get_object_reference('__export__', 'pti_order_method_s')[1]
            if partner_obj[0].is_consignment:
                order_method_id = ir_model_data.get_object_reference('__export__', 'pti_order_method_c')[1]          
            elif partner_obj[0].ref == 'tmp.customer':        
                order_method_id = ir_model_data.get_object_reference('__export__', 'pti_order_method_c')[1]     
            else:
                order_method_id = order_method_id
            vals = { 
                    'partner_id':partner_obj.id,
                    'order_method':order_method_id,
                    'warehouse_id':warehouse_obj.id,
                    'order_line':lines,
                    }
            sale_ids = self.env['sale.order'].create(vals)
            for a in invoice_id:
                if a.number[6:8] == '10':
                    a.write({'parama_so_id':sale_ids[0].id})
                    for line in a.invoice_line_ids:
                        line_ids = self.env['sale.order.line'].search([('product_id','=',line.product_id.id),('order_id','=',sale_ids[0].id)])
                        if line_ids:
                            line_ids[0].write({'product_uom_qty':line_ids.product_uom_qty + line.quantity})
                        else:
                            self.env['sale.order.line'].create({
                                                                'product_id':line.product_id.id,
                                                                'name': line.product_id.name,
                                                                'product_uom_qty':line.quantity,
                                                                'order_id':sale_ids[0].id
                                                                })
        
        return {
                'name': _('PRM Sale Order'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order',
                'res_id': sale_ids[0].id,
                'view_id': False,
                'view_type': 'form',
                'view_mode': 'form',
                'type': 'ir.actions.act_window',
                'target': 'current'
            }
