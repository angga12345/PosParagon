from openerp import models, fields, api


class batch_number(models.Model):
    _inherit = 'account.bank.statement.line'

    batch_number = fields.Char('Batch Number')


class make_payment_wizard(models.TransientModel):
    _inherit = 'pos.make.payment'
    
    @api.model
    def _default_journal_cash_only(self):
        session = False
        order_obj = self.env['pos.order']
        context = self._context
        active_id = context.get('active_id',False)
        print active_id
        if active_id:
            order = order_obj.browse(active_id)
            session = order.session_id
            print session
        if session:
            for journal in session.config_id.journal_ids:
                if journal.type == 'cash':
                    return journal.id
        return False
    
    journal_id = fields.Many2one('account.journal','Payment Mode',
                                    default=_default_journal_cash_only)
    batchno = fields.Char('Batch Number', size=17 )
    is_bank = fields.Boolean('is bank ? ')

    @api.onchange('journal_id')
    def journal_change(self):
        
        if self.journal_id :
            if self.journal_id.type == 'bank' :
                self.is_bank = 1
                
                
            else : 
                self.is_bank = 0
                
        
