from openerp import models, fields, api


class store_stock(models.Model):
    _name = "store.qoh"
    _description = "Store Stock"
    _template = 'pti_pos_stock_print.store_stock_report_view'
    
    def run_sql_store_name(self):
        store_name = ''
        uid = self.env.user.id
        self._cr.execute('''
                select pos_config.name
                from res_users
                left join pos_session on res_users.id = pos_session.user_id
                left join pos_config on pos_session.config_id = pos_config.id
                where pos_session.state='opened' and res_users.id = %s''',(uid,))
        _res = self._cr.fetchall()
        for res in _res:
            store_name = res[0]
        return store_name
    
    def run_sql(self):
        res_prod = []
        uid = self.env.user.id
        self._cr.execute('''
                with
                loc_id as
                (select stock_location.id as id, stock_location.complete_name as name
                from res_users
                left join pos_session on res_users.id = pos_session.user_id
                left join pos_config on pos_session.config_id = pos_config.id
                left join stock_location on pos_config.stock_location_id = stock_location.id
                where pos_session.state='opened' and res_users.id = %s)
                
                select product_template.name, stock_quant.qty
                from stock_quant
                left join product_template on stock_quant.product_id = product_template.id
                left JOIN loc_id loc ON stock_quant.location_id = loc.id
                where stock_quant.location_id = loc.id
                order by product_template.name desc''',(uid,))
        _res = self._cr.fetchall()
        for res in _res:
            prod = res[0]+'  Qty : '+str(res[1])
            res_prod.append(prod)
        return res_prod
    
    @api.multi
    def do_print(self):
        return self.env['report'].get_action(self, 'pti_pos_stock_print.store_stock_report_view')
store_stock()