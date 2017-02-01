from openerp import models, fields, api


class account_bank_statement_line(models.Model):
    _inherit = 'account.bank.statement.line'

    trace_no = fields.Char('Trace No.')
    appr_code = fields.Char('Appr. Code')
    
class make_payment_wizard(models.TransientModel):
    _inherit = 'pos.make.payment'

    traceno = fields.Char('Trace No.')
    apprcode = fields.Char('Appr. Code')