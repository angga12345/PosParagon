from openerp import api, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _process_order(self, order):
        session_obj = self.env['pos.session']
        # get session based on order
        order_session = session_obj.browse(order['pos_session_id'])
        # get config_id / pos store based on the order session
        order_config_id = order_session.config_id.id
        # search session which opened and the config_id / pos store same with order_config_id
        opened_session = session_obj.search([('config_id', '=', order_config_id), ('state', '=', 'opened')], limit=1)
        order['pos_session_id'] = opened_session.id
        print order
        return super(PosOrder, self)._process_order(order)
