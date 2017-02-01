from openerp import models, fields, api, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    loyalty_program_ids = fields.Many2many('loyalty.program',
                                           'loyalty_program_rel',
                                           'loyalty_program_id',
                                           'config_id',
                                           string='Loyalty Programs')
