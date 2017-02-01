from openerp import models, fields, api, _
from openerp.exceptions import Warning


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.multi
    def open_existing_session_cb_close(self):
        obj_ba = self.env['res.users'].has_group('pti_pos_pricelist_discount.BA_group')

        if obj_ba:
            for rec in self:
                if not rec.current_session_id.check:
                    raise Warning("Sorry You cannot close this session\n Please close and confirm the POS Screen first")
        return super(PosConfig, self).open_existing_session_cb_close()

    @api.multi
    def open_ui(self):
        for rec in self:
            rec.current_session_id.write({'check': False})
        return super(PosConfig, self).open_ui()


class PosSession(models.Model):
    _inherit = 'pos.session'

    check = fields.Boolean(default=False)

    @api.multi
    def confirm_close(self):
        for rec in self:
            rec.write({'check': True})
