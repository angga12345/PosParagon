from openerp import models, fields, api, _
from openerp.exceptions import UserError

class assign_collect_wizard(models.TransientModel):
    _name = 'assign.collector.wizard'
    
    collector_id = fields.Many2one('res.partner',string='collector', domain=[('is_collector', '=', True)])
    
    @api.multi
    def assign_collector(self, values):
        self.ensure_one()
        obj = self.env['account.move.line'].search([('id','=',values.get('active_id'))])
        if obj.collector_validated:
            raise UserError(_("Collector already validated."))
        else:
            obj.write({'collector_validated' : True,
                       'collector_id' : self.collector_id.id })