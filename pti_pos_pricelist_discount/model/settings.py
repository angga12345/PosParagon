from openerp.osv import fields, osv

class setting_inventory(osv.TransientModel):
    _inherit = 'stock.config.settings'

    def update_setting(self, cr, uid, **args):
        ids = self.search(cr, uid, [])
        cfg = {
            'group_stock_multiple_locations': 1,
            'group_stock_adv_location': 1,
            'group_uom': 1
        }
        if ids:
            o = self.browse(cr, uid, ids[-1])
            o.write(cfg)
            o.execute()
        else:
            id2 = self.create(cr, uid, cfg)
            self.browse(cr, uid, id2).execute()
        return True
    
class setting_sales(osv.TransientModel):
    _inherit = 'sale.config.settings'

    def update_setting(self, cr, uid, **args):
        ids = self.search(cr, uid, [])
        cfg = {
            'group_uom': 1, 
            'sale_pricelist_setting': 'formula'
        }
        if ids:
            o = self.browse(cr, uid, ids[-1])
            o.write(cfg)
            o.execute()
        else:
            id2 = self.create(cr, uid, cfg)
            self.browse(cr, uid, id2).execute()
        return True