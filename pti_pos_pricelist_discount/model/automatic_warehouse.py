from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError
import logging
_log = logging.getLogger(__name__)
import openerp.addons.decimal_precision as dp


# loyalty program
class loyalty_program(models.Model):
    _inherit = 'loyalty.program'
    dc_id = fields.Many2one('res.partner', 'Distribution Center')

# product pricelist
class product_pricelist(models.Model):
    _inherit = "product.pricelist"
    
    dc_id = fields.Many2one('res.partner', 'Distribution Center')


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    membership_pricelists = fields.Many2many('member.types', 'membership_type_rel', 'pricelist_item_id', string="Membership Discounts")
    shop_identifier_promo_period = fields.Char('Shop Identifier Period')
    sku_number_period = fields.Char(string='SKU Number Period', readonly=True)
    is_pos = fields.Boolean(string="For Point Of Sale", default=False)

    @api.model
    def create(self, values):
        values.update(self._check_shop_identifier(values))
        return super(ProductPricelistItem, self).create(values)

    @api.multi
    def write(self, values):
        values.update(self._check_shop_identifier(values))
        return super(ProductPricelistItem, self).write(values)
    
    def _check_shop_identifier(self, values):
        static_code, barcode, result = '2300', dict(), dict()

        if values.get('shop_identifier_promo_period'):
            field_key = 'sku_number_period'
            shop_identity = 'shop_identifier_promo_period'
            barcode[field_key] = str(static_code + values[shop_identity])
            result = \
                self._checksum_calculation(barcode, field_key, shop_identity)

        return result
    
    def _checksum_calculation(self, barcode, field_key, shop_identity):
        if len(barcode[field_key]) != 12:
            raise UserError(_('Invalid length for %s field must be 8 digits'
                              % (shop_identity)))

        odd_sum = 0
        even_sum = 0
        for i, char in enumerate(barcode[field_key]):
            j = i + 2
            if j % 3 == 0:
                even_sum += int(char)
            else:
                odd_sum += int(char)

        total_sum = (odd_sum * 3) + even_sum
        check_digit = 10 - total_sum % 10
        if check_digit == 10:
            check_digit = 0

        barcode.update({
            field_key: barcode[field_key] + str(check_digit)
        })

        return barcode
    
# res users
class res_users(models.Model):
    _inherit = 'res.users'
    
    password_temporer = fields.Char('Password temporer')
    allow_edit_price = fields.Boolean('Allow edit price', default=True)

    @api.model
    def create(self, values):
        user_id = super(res_users, self).create(values)
        ba_group_id = self.env.ref('pti_pos_pricelist_discount.BA_group').id
        if ba_group_id in user_id.groups_id.ids:
            ba_code_seq = self.env['ir.sequence'].next_by_code('ba.code.seq')
            user_id.partner_id.write({'ba_code': ba_code_seq})
        return user_id

    @api.multi
    def write(self, values):
        res = super(res_users, self).write(values)
        ba_group_id = self.env.ref('pti_pos_pricelist_discount.BA_group').id
        if ba_group_id in self.groups_id.ids:
            if not self.partner_id.ba_code:
                ba_code_seq = self.env['ir.sequence'].next_by_code('ba.code.seq')
                self.partner_id.write({'ba_code': ba_code_seq})
        return res

# pos session
class pos_session(models.Model):
    _inherit = 'pos.session'
     
    shop_identifier_origin = fields.Char(related='config_id.sku_number_origin', readonly=True, string='Shop Identifier origin', store=True)
    shop_identifier_period = fields.Char(related='config_id.sku_number_period', readonly=True, string='Shop Identifier period', store=True)
    categ_shop = fields.Char(related='config_id.cat_store_text', readonly=False, string='Categ Shop', store=True)
    store_code_in_session = fields.Char(related='config_id.stock_location_id.partner_id.store_code', readonly=True, string='Store Code In Session')

    @api.one
    @api.onchange('config_id')
    def _onchange_config_id(self):
        if self.config_id:
            if not self.config_id.stock_location_id:
                pos_name = self.config_id.name
                self.config_id = False
                raise ValidationError(_("%s Point of Sale didn't has Stock Location value. Please filled Stock Location value in %s Point of Sale"
                                  % (pos_name, self.config_id.name)))

    @api.model
    def create(self, values):
        session_id = super(pos_session, self).create(values)
        if session_id:
            config_id = self.env['pos.config'].browse(session_id.config_id.id)
            inc_seq = config_id.sequence_number + 1
            config_id.write({'sequence_number': inc_seq})
        return session_id


class pos_order_line(models.Model):
    _inherit = "pos.order.line"

    #Add fields Discount By PTI and Discount by MDS
    diskon_pti = fields.Float(string='Diskon Ditanggung PTI (%)', digits=dp.get_precision('Discount'))
    diskon_mds = fields.Float(string='Diskon Ditanggung MDS (%)', digits=dp.get_precision('Discount'))
    #garapan anisa end
    price_subtotal_incl_rel = fields.Float(related='price_subtotal_incl', string='Amount Total', store=True)
    price_subtotal_rel = fields.Float(related='price_subtotal', string='Total without tax', store=True)   
    pricelist_item_id = fields.Many2one('product.pricelist.item', String="Pricelist Item")
    #Add onchange that depends on Nilai Diskon Ditanggung PTI and Nilai Diskon Ditanggung MDS.
    @api.onchange('diskon_pti','diskon_mds')
    def _onchange_discount(self):
        if self.diskon_mds and self.diskon_pti:
            self.discount = self.diskon_pti + self.diskon_mds

        
# pos order : pos
class pos_order(models.Model):
    _inherit = "pos.order"
    shop_identifier_origin = fields.Char('Shop Identifier Origin')
    shop_identifier_period = fields.Char('Shop Identifier Period')
    seq_num = fields.Integer('Sequences')
    rel_cat_shop = fields.Char(related='session_id.categ_shop', readonly=True, string='Categ Shop', store=True)
    amount_total_rel = fields.Float(related='amount_total', string='Amount Total', store=True)
    flag = fields.Boolean(string='Flag')
    loyalty_reward_id = fields.Many2one('loyalty.reward', string="Loyalty Reward")

    @api.one
    def increment_seq_number(self):
        global seq_number
        config_seq = self.config_id.sequence_number
        self.seq_num = config_seq
        last_pos_ref = self.get_last_pos_ref(self.session_id.config_id.id)
        last_pos_ref = str(last_pos_ref.get('last_id', 0))
        seq_number = last_pos_ref[len(last_pos_ref) - 5:len(last_pos_ref)]
        # jika sequence number = 'e'
        if seq_number == 'e':
            return
        self.config_id.write({
                          'sequence_number': int(seq_number) + 1,
                          })

    def get_last_pos_ref(self, config_id):
        last_session_id = self.get_last_session_id([config_id])
        last_session_id = str(last_session_id.get('last_id', 0))
        # menampilkan pos session yang sekarang dan pos config yang aktif dan filter pos reference yang ada saja
        self.env.cr.execute('select MAX(pos_reference) as last_id from pos_order po, pos_session ps, pos_config pc '
                        'where po.session_id = %s  and ps.config_id = %s and po.pos_reference IS NOT NULL',
                        (last_session_id, config_id))

        result = self.env.cr.dictfetchall()
        return result[0]

    def get_last_session_id(self, config_id):
        # menampilkan pos session id dari pos order yang sama dengan pos session id
        last_session_id = """
        SELECT MAX(ps.id) as last_id
        FROM pos_session ps, pos_order po
        WHERE po.session_id = ps.id
        """
        self.env.cr.execute('SELECT MAX(ps.id) as last_id '
                            'FROM pos_session ps, pos_order po '
                            'WHERE po.session_id = ps.id and '
                            'ps.config_id = %s',
                            (config_id))
        result = self.env.cr.dictfetchall()
        return result[0]


    # inherit create
    def create(self, cr, uid, values, context=None):
        ids = super(pos_order, self).create(cr, uid, values, context=context)
        if values.get('session_id'):
            # set name based on the sequence specified on the config
            session = self.pool['pos.session'].browse(cr, uid, values['session_id'], context=context)   
            values['name'] = session.config_id.sequence_id._next()
            values.setdefault('session_id', session.config_id.pricelist_id.id)
            self.increment_seq_number(cr, uid, ids, context)
                
        else:
            # fallback on any pos.order sequence
            values['name'] = self.pool.get('ir.sequence').next_by_code(cr, uid, 'pos.order', context=context)
            self.increment_seq_number(cr, uid, ids, context)
                
        return ids
    
# pos config
class pos_config(models.Model):
    _inherit = "pos.config"

    category_shop = fields.Selection([('stand_alone', 'Stand Alone'), ('shop_in_shop', 'Shop in Shop'), ('shop_in_shop_mds', 'Shop in Shop MDS')], 'Category Shop')
    shop_identifier_promo_period = fields.Char('Shop Identifier Period')
    sku_number_period = fields.Char(string='SKU Number Period', readonly=True)
    shop_identifier_origin = fields.Char('Shop Identifier Origin')
    sku_number_origin = fields.Char(string='SKU Number Origin', readonly=True)
    tags = fields.Many2one('product.brand', string="Tags")
    sequence_number = fields.Integer('Order Sequence Number', default=1)
    cat_store_text = fields.Char('Kategori Store Text')
    text = fields.Text(related="tags.text", string="Brand Text")
    ads = fields.Text(string="Category Text")
    partner_id = fields.Many2one('res.partner' , domain="[('is_shop', '=', True )]" , string="Customer")
    stand_alone_categ = fields.Selection([('wbh', 'WBH Store'),('independent', 'Independent Store')], 'Stand Alone Category')
    
    @api.onchange('partner_id')
    @api.model
    def set_stock_location(self):
#         if self.partner_id.customer:
#             if self.partner_id.is_consignment:
#                 customer_id = self.env['stock.warehouse'].search(['stock_location_id','=',self.stock_location_id.id])
#                 self.partner_id=customer_id.id
#         else:
        stock_location = self.env['stock.location'].search([('partner_id','=',self.partner_id.id)], limit=1)
        self.stock_location_id=stock_location.id
    
    @api.onchange('category_shop')
    def do_changes(self):
        if self.category_shop:
            self.cat_store_text = self.category_shop

    @api.model
    def create(self, values):
        values.update(self._check_shop_identifier(values))
        return super(pos_config, self).create(values)

    @api.multi
    def write(self, values):
        values.update(self._check_shop_identifier(values))
        return super(pos_config, self).write(values)

    def _check_shop_identifier(self, values):
        static_code, barcode, result = '2300', dict(), dict()

        if values.get('shop_identifier_promo_period'):
            field_key = 'sku_number_period'
            shop_identity = 'shop_identifier_promo_period'
            barcode[field_key] = str(static_code + values[shop_identity])
            result = \
                self._checksum_calculation(barcode, field_key, shop_identity)
        if values.get('shop_identifier_origin'):
            field_key = 'sku_number_origin'
            shop_identity = 'shop_identifier_origin'
            barcode[field_key] = str(static_code + values[shop_identity])
            result = \
                self._checksum_calculation(barcode, field_key, shop_identity)

        return result

    def _checksum_calculation(self, barcode, field_key, shop_identity):
        if len(barcode[field_key]) != 12:
            raise UserError(_('Invalid length for %s field must be 8 digits'
                              % (shop_identity)))

        odd_sum = 0
        even_sum = 0
        for i, char in enumerate(barcode[field_key]):
            j = i + 2
            if j % 3 == 0:
                even_sum += int(char)
            else:
                odd_sum += int(char)

        total_sum = (odd_sum * 3) + even_sum
        check_digit = 10 - total_sum % 10
        if check_digit == 10:
            check_digit = 0

        barcode.update({
            field_key: barcode[field_key] + str(check_digit)
        })

        return barcode
    @api.multi
    def open_ui(self):
        ui = super(pos_config, self).open_ui()
        for session in self:
            if not session.stock_location_id:
                raise ValidationError(_("This Point Of Sale didn't have Stock Location, please filled the Stock Location"))
        return ui

    @api.multi
    def open_session_cb(self):
        ui = super(pos_config, self).open_session_cb()
        for session in self:
            if not session.stock_location_id:
                raise ValidationError(_("This Point Of Sale didn't have Stock Location, please filled the Stock Location"))
        return ui


class location(models.Model):
    _inherit = "stock.location"
    shop_id = fields.Many2one('res.partner', 'Shop')


class warehouse(models.Model):
    _inherit = "stock.warehouse"
    shop_id = fields.Many2one('res.partner', 'Shop')


class partner(models.Model):
    _inherit = "res.partner" 
    is_shop = fields.Boolean('Is a Shop', help="Check this box if this partner is a Shop.")
    store_code = fields.Char('Store Code ID')
    ba_code = fields.Char('Ba Code ID')
    category_shop = fields.Selection([('stand_alone', 'Stand Alone'), ('shop_in_shop', 'Shop in Shop'), ('shop_in_shop_mds', 'Shop in Shop MDS')], 'Category Shop')
    shop_identifier_origin = fields.Char('Shop Identifier Origin')

    @api.onchange('is_shop', 'name')
    def do_changes(self):
        if self.is_shop:
            self.company_type = 'company'
            self.customer = False
            self.category_shop = 'stand_alone'

    def getAccountJournals(self):
        res = []  # array
        a = self.env['account.journal'].search([('journal_user', '=', True)])
        for i in a:
            res.append(i.id)
        return res

    @api.model
    def create(self, values):
        res = super(partner, self).create(values)
        if values.get('is_shop'):
            values['store_code'] = self.env['ir.sequence'].next_by_code('store.code.seq')
            shop = res.CreatePosConfigByShop()
            if values.get('customer'):
                if values.get('is_consignment'):
                    stock_location = self.get_stock_location(res)
                    shop.write({'partner_id': res.id,
                                'stock_location_id': stock_location.id
                                })
        return res

    @api.multi
    def write(self, values):
        for this in self:
            is_shop_old = this.is_shop
            is_shop_new = values.get('is_shop', False)
            store_code = this.store_code
            if (is_shop_old or is_shop_new) and not store_code:
                values['store_code'] = self.env['ir.sequence'].next_by_code('store.code.seq')
            elif values.get('is_shop') is False:
                values['category_shop'] = False
                values['store_code'] = False
                values['shop_identifier_origin'] = False
        res = super(partner, self).write(values)
        if values.get('is_shop'):
            shop = self.CreatePosConfigByShop()
            stock_location = self.get_stock_location(this)
            shop.write({'partner_id': self.id,
                        'stock_location_id': stock_location.id
                        })
        return res

    def get_stock_location(self, partner_id):
        stock_location = self.env['stock.location'].search([('partner_id', '=', partner_id.id), ('name', '=', 'Stock')],limit=1)
        return stock_location
#     @api.model
#     def CreateSettings(self):
#         for partner in self:
#             if partner.this_for_all:
#                 if partner.is_consignment or partner.is_team_leader:
#                     raise UserError (_("Main company can't as consignment or TL."))
#             elif partner.is_dc:
#                 if not partner.ref:
#                     raise UserError(_('Fill Internal Reference for DC first.(in Tab Sale & Purchases)'))
#                 wh_exist = self.env['stock.warehouse'].search(['|', ('name', '=', partner.name), ('code', '=', partner.ref or '-')])
#                 if wh_exist:
#                     return
#                 wh_vals = {
#                     'name' : partner.name,
#                     'code' : partner.ref,
#                     'dc_id' : partner.id,
#                     'partner_id' : partner.id
#                 }
#                 new_wh = self.env['stock.warehouse'].create(wh_vals)
#                 if len(new_wh) == 0:
#                     raise UserError(_("Ups, cannot create warehouse %s" % (partner.name)))
#                 ir_model_obj = self.pool['ir.model.data']
#                 type_obj = self.env['stock.picking.type']
#                 loc_obj = self.env['stock.location']
#                 seq_in = new_wh.in_type_id.sequence_id
#                 seq_out = new_wh.out_type_id.sequence_id
#                 view_location = new_wh.view_location_id
#                 stock_location = new_wh.lot_stock_id
# 
#                 # RENAME VIEW LOCATION
#                 # for DC's warehouse, fill partner_id = dc_id
#                 view_location.write({
#                     'name': partner.name,
#                     'partner_id': partner.id,
#                     'dc_id': partner.id
#                 })
# 
#                 # update stock location, fill partner_id = dc_id
#                 stock_location.write({
#                     'partner_id': partner.id,
#                     'dc_id': partner.id
#                 })                
# 
#                 # GET INFORMATION NDC
#                 model, ndc_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'stock', 'warehouse0')
#                 NDC = self.env['stock.warehouse'].search([('id', '=', ndc_id)])
#                 NDC_Delivery = NDC.out_type_id
# 
#                 model, customers_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'stock', 'stock_location_customers')
#                 model, ndc_transit_qua_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'pti_stock_default_mto', 'ndc_transit_quarantine')
#                 model, ndc_stag_loc_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'pti_stock_default_mto', 'ndc_staging')
#                 model, pick_tran_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'pti_stock_default_mto', 'picking_quarantine')
#                 model, ndc_quarantine_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'pti_stock_default_mto', 'ndc_quarantine')
# 
#                 for l in ['Transit', 'Quarantine', 'Bad Products']:
#                     loc = loc_obj.create({
#                         'name' : l,
#                         'location_id': view_location.id,
#                         'usage': 'internal',
#                         'active': True,
#                         'partner_id': partner.id,
#                         'dc_id': partner.id
#                     })
#                     if l == 'Quarantine':
#                         # CREATE OPERATION CUSTOMERS TO DISTRIBUTION CENTER
#                         type_customer = type_obj.create({
#                             'name' : 'Customers to %s' % (partner.name,),
#                             'default_location_src_id': customers_id,
#                             'default_location_dest_id': loc.id,
#                             'sequence_id': seq_in.id,
#                             'warehouse_id': new_wh.id,
#                             'code' : 'internal'
#                         })
#                         new_wh.out_type_id.write({
#                             'return_picking_type_id': type_customer.id
#                         })
#                         # CREATE OPERATION DC TO NDC
#                         type_obj.create({
#                             'name': '%s to NDC' % (partner.name,),
#                             'default_location_src_id': loc.id,
#                             'default_location_dest_id': ndc_transit_qua_id,
#                             'sequence_id': seq_out.id,
#                             'warehouse_id': new_wh.id,
#                             'code' : 'internal'
#                         })
#                     if l == 'Transit':
#                         # CREATE OPERATION TRANSIT FROM DISTRIBUTION CENTER
#                         type_transit = type_obj.create({
#                             'name': 'Receipts from %s' % (NDC.name,),
#                             'default_location_src_id': loc.id,
#                             'default_location_dest_id': stock_location.id,
#                             'sequence_id': seq_in.id,
#                             'warehouse_id': new_wh.id,
#                             'code': 'internal'
#                         })
#                         new_wh.in_type_id.write({
#                             'name': 'NDC to %s' % (partner.name,),
#                             'code': 'internal',
#                             'sequence_id': NDC_Delivery.sequence_id.id,
#                             'warehouse_id': NDC.id,
#                             'apply_mto': True,
#                             'default_location_src_id': ndc_stag_loc_id,
#                             'default_location_dest_id': loc.id
#                         })
#                         # PREPARE ROUTE AND PUSH RULES
#                         routes = self.env['stock.location.route']
#                         path = self.env['stock.location.path']
#                         routes_id = routes.search([('name' , '=', 'PTI ROUTES')], limit=1)
#                         if len(routes_id) == 0:
#                             res = routes.create({
#                                 'name': 'PTI ROUTES',
#                                 'active': True,
#                                 'warehouse_selectable': True
#                             })
#                             path.create({
#                                 'route_id': res.id,
#                                 'name': 'transit to %s' % (partner.name,),
#                                 'location_from_id': loc.id,
#                                 'location_dest_id': stock_location.id,
#                                 'picking_type_id': type_transit.id,
#                                 'active': True
#                             })
#                             
#                             partner.addWarehouse(res.id, new_wh.id)
#                             partner.addWarehouse(res.id, NDC.id)
#                         else:
#                             exist = path.search([('location_from_id', '=', loc.id), ('location_dest_id', '=', stock_location.id)])
#                             if not exist.id:
#                                 path.create({
#                                     'route_id': routes_id.id,
#                                     'name': 'transit to %s' % (partner.name,),
#                                     'location_from_id': loc.id,
#                                     'location_dest_id': stock_location.id,
#                                     'picking_type_id': type_transit.id,
#                                     'active': True
#                                 })
# 
#                                 partner.addWarehouse(routes_id.id, new_wh.id)
#                                 
#             #####STAND ALONE#########
#             elif partner.is_shop and partner.category_shop == 'stand_alone':
#                 if not partner.ref:
#                     raise UserError(_('Fill Internal Reference for SHOP first.(in Tab Sale & Purchases)'))
#                 if not partner.dc_id:
#                     raise UserError(_('Fill Distribution center and Category Shop for SHOP first.'))
#                 if not partner.category_shop:
#                     raise UserError(_('Fill Category Shop for SHOP first.'))
#                  
#                 wh_exist = self.env['stock.warehouse'].search(['|', ('name', '=', partner.name), ('code', '=', partner.ref or '-')])
#                 if wh_exist:
#                     return
#                 wh_vals = {
#                     'name' : partner.name,
#                     'code' : partner.ref,
#                     'shop_id' : partner.id,
#                     'partner_id' : partner.id
#                 }
#                 new_wh = self.env['stock.warehouse'].create(wh_vals)
#                 if len(new_wh) == 0:
#                     raise UserError(_("Ups, cannot create warehouse %s" % (partner.name)))
#                 ir_model_obj = self.pool['ir.model.data']
#                 config_obj = self.env['pos.config']
#                 type_obj = self.env['stock.picking.type']
#                 loc_obj = self.env['stock.location']
#                 ref_seq_posorders = type_obj.search([('name', '=', 'PoS Orders')])
#                 ref_seq_posorders_id = ref_seq_posorders.sequence_id.id
#                 seq_in = new_wh.in_type_id.sequence_id
#                 seq_out = new_wh.out_type_id.sequence_id
#                 view_location = new_wh.view_location_id
#                 stock_location = new_wh.lot_stock_id
#   
#                 # RENAME VIEW LOCATION
#                 # for DC's warehouse, fill partner_id = dc_id
#                 view_location.write({
#                     'name': partner.name,
#                     'partner_id': partner.id,
#                     'shop_id': partner.id
#                 })
#   
#                 # update stock location, fill partner_id = dc_id
#                 stock_location.write({
#                     'partner_id': partner.id,
#                     'shop_id': partner.id
#                 })                
#   
#                  
#                 model, customers_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'stock', 'stock_location_customers')
#  
#                 # GET INFORMATION DC
#                 DC = self.env['stock.warehouse'].search([('name', '=', partner.dc_id.name)])
#                 DC_Delivery = DC.out_type_id
# 
#                 #
#                 loc_dc_stock = self.env['stock.location'].search([('partner_id', '=', partner.id), ('name', '=', 'Stock')])
#                 loc_dc_stock_id = loc_dc_stock.id
# 
#                 #
#                 loc_posorder_stock = self.env['stock.location'].search([('partner_id', '=', partner.id), ('name', '=', 'Stock')])
#                 loc_posorder_stock_id = loc_posorder_stock.id
# 
#                 #
#                 loc_dc_quarantine = self.env['stock.location'].search([('dc_id', '=', partner.dc_id.id), ('name', '=', 'Quarantine')])
#                 loc_dc_quarantine_id = loc_dc_quarantine.id
# 
#                  
#                  
#                 # CREATE OPERATION POSORDERS SHOP
#                 type_obj.create({
#                     'name' : 'PoS Orders %s' % (partner.name,),
#                     'default_location_src_id': loc_posorder_stock_id,
#                     'default_location_dest_id': customers_id,
#                     'sequence_id': ref_seq_posorders_id,
#                     'warehouse_id': '',
#                     'code' : 'outgoing'
#                 })
#                  
#                 # stock picking id
#                 name_pick_tp = 'PoS Orders ' + str(partner.name)
#                 stock_pick_type_id = self.env['stock.picking.type'].search([('name', '=', name_pick_tp)])
#                 pos_stock_pick_type_id = stock_pick_type_id.id
#                 pos_stock_pick_type_loc_src_id = loc_posorder_stock_id  # stock_pick_type_id.default_location_src_id.id
# 
#                  
#                  
#                 # CREATE OPERATION POINT OF SALES
#                 id = config_obj.create({
#                     'name' : '%s' % (partner.name,),
#                     'picking_type_id': pos_stock_pick_type_id,
#                     'stock_location_id': pos_stock_pick_type_loc_src_id,
#                     'category_shop': 'stand_alone',
#                     'cat_store_text': 'stand_alone',
#                 })
# 
#                 id.write({'journal_ids': [(6, 0, self.getAccountJournals())], })
#                      
#                 for l in ['Transit', 'Quarantine', 'Bad Products']:
#                     loc = loc_obj.create({
#                         'name' : l,
#                         'location_id': view_location.id,
#                         'usage': 'internal',
#                         'active': True,
#                         'partner_id': partner.id,
#                         'shop_id': partner.id
#                     })
#                      
#                          
#                     if l == 'Quarantine':
#                         # CREATE OPERATION SHOP to DC
#                         type_obj.create({
#                             'name': '%s to %s' % (partner.name, partner.dc_id.name,),
#                             'default_location_src_id': loc.id,
#                             'default_location_dest_id': loc_dc_quarantine_id,
#                             'sequence_id': seq_out.id,
#                             'warehouse_id': new_wh.id,
#                             'code' : 'internal'
#                         })
#                     if l == 'Transit':
#                         # CREATE OPERATION TRANSIT FROM DISTRIBUTION CENTER/SHOP (DC to SHOP)
#                         type_transit = type_obj.create({
#                             'name': 'Receipts from %s' % (DC.name,),
#                             'default_location_src_id': loc.id,
#                             'default_location_dest_id': stock_location.id,
#                             'sequence_id': seq_in.id,
#                             'warehouse_id': new_wh.id,
#                             'code': 'internal'
#                         })
#                         new_wh.in_type_id.write({
#                             'name': '%s to %s' % (partner.dc_id.name, partner.name,),
#                             'code': 'internal',
#                             'sequence_id': DC_Delivery.sequence_id.id,
#                             'warehouse_id': DC.id,
#                             # 'apply_mto': True,
#                             'default_location_src_id': DC_Delivery.default_location_src_id.id,
#                             'default_location_dest_id': loc.id
#                         })
#                         # PREPARE ROUTE AND PUSH RULES
#                         routes = self.env['stock.location.route']
#                         path = self.env['stock.location.path']
#                         routes_id = routes.search([('name' , '=', 'PTI ROUTES')], limit=1)
#                         if len(routes_id) == 0:
#                             res = routes.create({
#                                 'name': 'PTI ROUTES',
#                                 'active': True,
#                                 'warehouse_selectable': True
#                             })
#                             path.create({
#                                 'route_id': res.id,
#                                 'name': 'transit to %s' % (partner.name,),
#                                 'location_from_id': loc.id,
#                                 'location_dest_id': stock_location.id,
#                                 'picking_type_id': type_transit.id,
#                                 'active': True
#                             })
#                                
#                             partner.addWarehouse(res.id, new_wh.id)
#                             partner.addWarehouse(res.id, DC.id)
#                         else:
#                             exist = path.search([('location_from_id', '=', loc.id), ('location_dest_id', '=', stock_location.id)])
#                             if not exist.id:
#                                 path.create({
#                                        'route_id': routes_id.id,
#                                        'name': 'transit to %s' % (partner.name,),
#                                        'location_from_id': loc.id,
#                                        'location_dest_id': stock_location.id,
#                                        'picking_type_id': type_transit.id,
#                                        'active': True
#                                 })
#      
#                                 partner.addWarehouse(routes_id.id, new_wh.id)
#             #
#             #####SHOP IN SHOP########
#             elif partner.is_shop and partner.category_shop == 'shop_in_shop':
#                 if not partner.ref:
#                     raise UserError(_('Fill Internal Reference for SHOP first.(in Tab Sale & Purchases)'))
#                 if not partner.dc_id:
#                     raise UserError(_('Fill Distribution center and Category Shop for SHOP first.'))
#                 if not partner.category_shop:
#                     raise UserError(_('Fill Category Shop for SHOP first.'))
#                 if not partner.shop_identifier_origin:
#                     raise UserError(_('Fill Shop Identifier Origin for SHOP first.'))
#                 wh_exist = self.env['stock.warehouse'].search(['|', ('name', '=', partner.name), ('code', '=', partner.ref or '-')])
#                 if wh_exist:
#                     return
#                 wh_vals = {
#                     'name' : partner.name,
#                     'code' : partner.ref,
#                     'shop_id' : partner.id,
#                     'partner_id' : partner.id
#                 }
#                 new_wh = self.env['stock.warehouse'].create(wh_vals)
#                 if len(new_wh) == 0:
#                     raise UserError(_("Ups, cannot create warehouse %s" % (partner.name)))
#                 ir_model_obj = self.pool['ir.model.data']
#                 config_obj = self.env['pos.config']
#                 type_obj = self.env['stock.picking.type']
#                 loc_obj = self.env['stock.location']
#                 ref_seq_posorders = type_obj.search([('name', '=', 'PoS Orders')])
#                 ref_seq_posorders_id = ref_seq_posorders.sequence_id.id
#                 seq_in = new_wh.in_type_id.sequence_id
#                 seq_out = new_wh.out_type_id.sequence_id
#                 view_location = new_wh.view_location_id
#                 stock_location = new_wh.lot_stock_id
#   
#                 # RENAME VIEW LOCATION
#                 # for DC's warehouse, fill partner_id = dc_id
#                 view_location.write({
#                     'name': partner.name,
#                     'partner_id': partner.id,
#                     'shop_id': partner.id
#                 })
#   
#                 # update stock location, fill partner_id = dc_id
#                 stock_location.write({
#                     'partner_id': partner.id,
#                     'shop_id': partner.id
#                 })                
#   
#                  
#                 model, customers_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'stock', 'stock_location_customers')
#  
#                 # GET INFORMATION DC
#                 DC = self.env['stock.warehouse'].search([('name', '=', partner.dc_id.name)])
#                 DC_Delivery = DC.out_type_id
# 
#                 #
#                 loc_dc_stock = self.env['stock.location'].search([('partner_id', '=', partner.id), ('name', '=', 'Stock')])
#                 loc_dc_stock_id = loc_dc_stock.id
# 
#                 #
#                 loc_posorder_stock = self.env['stock.location'].search([('partner_id', '=', partner.id), ('name', '=', 'Stock')])
#                 loc_posorder_stock_id = loc_posorder_stock.id
# 
#                 #
#                 loc_dc_quarantine = self.env['stock.location'].search([('dc_id', '=', partner.dc_id.id), ('name', '=', 'Quarantine')])
#                 loc_dc_quarantine_id = loc_dc_quarantine.id
#                  
#                 # journals
#                 # journals_type = self.env['account.journal'].search([('name','=','Customer Invoices'),('type','=','sale')])
#                 # journals_type_id = journals_type 
#                  
#                 # CREATE OPERATION POSORDERS SHOP
#                 type_obj.create({
#                     'name' : 'PoS Orders %s' % (partner.name,),
#                     'default_location_src_id': loc_posorder_stock_id,
#                     'default_location_dest_id': customers_id,
#                     'sequence_id': ref_seq_posorders_id,
#                     'warehouse_id': '',
#                     'code' : 'outgoing'
#                 })
#                  
#                 # stock picking id
#                 name_pick_tp = 'PoS Orders ' + str(partner.name)
#                 stock_pick_type_id = self.env['stock.picking.type'].search([('name', '=', name_pick_tp)])
#                 pos_stock_pick_type_id = stock_pick_type_id.id
#                 pos_stock_pick_type_loc_src_id = loc_posorder_stock_id
#                  
#                 # CREATE OPERATION POINT OF SALES
#                 id = config_obj.create({
#                     'name' : '%s' % (partner.name,),
#                     'picking_type_id': pos_stock_pick_type_id,
#                     'stock_location_id': pos_stock_pick_type_loc_src_id,
#                     'category_shop': 'shop_in_shop',
#                     'cat_store_text': 'shop_in_shop',
#                     'shop_identifier_origin': partner.shop_identifier_origin,
#                     'iface_print_auto': False,
#                     'cash_control': False,
#                     'iface_print_via_proxy': False,
#                     'iface_scan_via_proxy': True,
#                     'iface_cashdrawer': False,
#                 })
#                 id.write({'journal_ids': [(6, 0, self.getAccountJournals())], })
#                      
#                 for l in ['Transit', 'Quarantine', 'Bad Products']:
#                     loc = loc_obj.create({
#                         'name' : l,
#                         'location_id': view_location.id,
#                         'usage': 'internal',
#                         'active': True,
#                         'partner_id': partner.id,
#                         'shop_id': partner.id
#                     })
#                      
#                          
#                     if l == 'Quarantine':
#                         # CREATE OPERATION SHOP to DC
#                         type_obj.create({
#                             'name': '%s to %s' % (partner.name, partner.dc_id.name,),
#                             'default_location_src_id': loc.id,
#                             'default_location_dest_id': loc_dc_quarantine_id,
#                             'sequence_id': seq_out.id,
#                             'warehouse_id': new_wh.id,
#                             'code' : 'internal'
#                         })
#                     if l == 'Transit':
#                         # CREATE OPERATION TRANSIT FROM DISTRIBUTION CENTER/SHOP (DC to SHOP)
#                         type_transit = type_obj.create({
#                             'name': 'Receipts from %s' % (DC.name,),
#                             'default_location_src_id': loc.id,
#                             'default_location_dest_id': stock_location.id,
#                             'sequence_id': seq_in.id,
#                             'warehouse_id': new_wh.id,
#                             'code': 'internal'
#                         })
#                         new_wh.in_type_id.write({
#                             'name': '%s to %s' % (partner.dc_id.name, partner.name,),
#                             'code': 'internal',
#                             'sequence_id': DC_Delivery.sequence_id.id,
#                             'warehouse_id': DC.id,
#                             # 'apply_mto': True,
#                             'default_location_src_id': DC_Delivery.default_location_src_id.id,
#                             'default_location_dest_id': loc.id
#                         })
#                         # PREPARE ROUTE AND PUSH RULES
#                         routes = self.env['stock.location.route']
#                         path = self.env['stock.location.path']
#                         routes_id = routes.search([('name' , '=', 'PTI ROUTES')], limit=1)
#                         if len(routes_id) == 0:
#                             res = routes.create({
#                                 'name': 'PTI ROUTES',
#                                 'active': True,
#                                 'warehouse_selectable': True
#                             })
#                             path.create({
#                                 'route_id': res.id,
#                                 'name': 'transit to %s' % (partner.name,),
#                                 'location_from_id': loc.id,
#                                 'location_dest_id': stock_location.id,
#                                 'picking_type_id': type_transit.id,
#                                 'active': True
#                             })
#                                
#                             partner.addWarehouse(res.id, new_wh.id)
#                             partner.addWarehouse(res.id, DC.id)
#                         else:
#                             exist = path.search([('location_from_id', '=', loc.id), ('location_dest_id', '=', stock_location.id)])
#                             if not exist.id:
#                                 path.create({
#                                        'route_id': routes_id.id,
#                                        'name': 'transit to %s' % (partner.name,),
#                                        'location_from_id': loc.id,
#                                        'location_dest_id': stock_location.id,
#                                        'picking_type_id': type_transit.id,
#                                        'active': True
#                                 })
#      
#                                 partner.addWarehouse(routes_id.id, new_wh.id)
#             #
#             #####SHOP IN SHOP MDS########
#             elif partner.is_shop and partner.category_shop == 'shop_in_shop_mds':
#                 if not partner.ref:
#                     raise UserError(_('Fill Internal Reference for SHOP first.(in Tab Sale & Purchases)'))
#                 if not partner.dc_id:
#                     raise UserError(_('Fill Distribution center and Category Shop for SHOP first.'))
#                 if not partner.category_shop:
#                     raise UserError(_('Fill Category Shop for SHOP first.'))
#                 if not partner.shop_identifier_origin:
#                     raise UserError(_('Fill Shop Identifier Origin for SHOP first.'))
#                 wh_exist = self.env['stock.warehouse'].search(['|', ('name', '=', partner.name), ('code', '=', partner.ref or '-')])
#                 if wh_exist:
#                     return
#                 wh_vals = {
#                     'name' : partner.name,
#                     'code' : partner.ref,
#                     'shop_id' : partner.id,
#                     'partner_id' : partner.id
#                 }
#                 new_wh = self.env['stock.warehouse'].create(wh_vals)
#                 if len(new_wh) == 0:
#                     raise UserError(_("Ups, cannot create warehouse %s" % (partner.name)))
#                 ir_model_obj = self.pool['ir.model.data']
#                 config_obj = self.env['pos.config']
#                 type_obj = self.env['stock.picking.type']
#                 loc_obj = self.env['stock.location']
#                 ref_seq_posorders = type_obj.search([('name', '=', 'PoS Orders')])
#                 ref_seq_posorders_id = ref_seq_posorders.sequence_id.id
#                 seq_in = new_wh.in_type_id.sequence_id
#                 seq_out = new_wh.out_type_id.sequence_id
#                 view_location = new_wh.view_location_id
#                 stock_location = new_wh.lot_stock_id
#   
#                 # RENAME VIEW LOCATION
#                 # for DC's warehouse, fill partner_id = dc_id
#                 view_location.write({
#                     'name': partner.name,
#                     'partner_id': partner.id,
#                     'shop_id': partner.id
#                 })
#   
#                 # update stock location, fill partner_id = dc_id
#                 stock_location.write({
#                     'partner_id': partner.id,
#                     'shop_id': partner.id
#                 })                
#   
#                  
#                 model, customers_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'stock', 'stock_location_customers')
#  
#                 # GET INFORMATION DC
#                 DC = self.env['stock.warehouse'].search([('name', '=', partner.dc_id.name)])
#                 DC_Delivery = DC.out_type_id
# 
#                 #
#                 loc_dc_stock = self.env['stock.location'].search([('partner_id', '=', partner.id), ('name', '=', 'Stock')])
#                 loc_dc_stock_id = loc_dc_stock.id
# 
#                 #
#                 loc_posorder_stock = self.env['stock.location'].search([('partner_id', '=', partner.id), ('name', '=', 'Stock')])
#                 loc_posorder_stock_id = loc_posorder_stock.id
# 
#                 #
#                 loc_dc_quarantine = self.env['stock.location'].search([('dc_id', '=', partner.dc_id.id), ('name', '=', 'Quarantine')])
#                 loc_dc_quarantine_id = loc_dc_quarantine.id
#                  
#                 # journals
#                 # journals_type = self.env['account.journal'].search([('name','=','Customer Invoices'),('type','=','sale')])
#                 # journals_type_id = journals_type 
#                  
#                 # CREATE OPERATION POSORDERS SHOP
#                 type_obj.create({
#                     'name' : 'PoS Orders %s' % (partner.name,),
#                     'default_location_src_id': loc_posorder_stock_id,
#                     'default_location_dest_id': customers_id,
#                     'sequence_id': ref_seq_posorders_id,
#                     'warehouse_id': '',
#                     'code' : 'outgoing'
#                 })
#                  
#                 # stock picking id
#                 name_pick_tp = 'PoS Orders ' + str(partner.name)
#                 stock_pick_type_id = self.env['stock.picking.type'].search([('name', '=', name_pick_tp)])
#                 pos_stock_pick_type_id = stock_pick_type_id.id
#                 pos_stock_pick_type_loc_src_id = loc_posorder_stock_id
#                  
#                 # CREATE OPERATION POINT OF SALES
#                 id = config_obj.create({
#                     'name' : '%s' % (partner.name,),
#                     'picking_type_id': pos_stock_pick_type_id,
#                     'stock_location_id': pos_stock_pick_type_loc_src_id,
#                     'category_shop': 'shop_in_shop_mds',
#                     'cat_store_text': 'shop_in_shop_mds',
#                     'shop_identifier_origin': partner.shop_identifier_origin,
#                     'iface_print_auto': False,
#                     'cash_control': False,
#                     'iface_print_via_proxy': False,
#                     'iface_scan_via_proxy': True,
#                     'iface_cashdrawer': False,
#                 })
#                 id.write({'journal_ids': [(6, 0, self.getAccountJournals())], })
#                      
#                 for l in ['Transit', 'Quarantine', 'Bad Products']:
#                     loc = loc_obj.create({
#                         'name' : l,
#                         'location_id': view_location.id,
#                         'usage': 'internal',
#                         'active': True,
#                         'partner_id': partner.id,
#                         'shop_id': partner.id
#                     })
#                      
#                          
#                     if l == 'Quarantine':
#                         # CREATE OPERATION SHOP to DC
#                         type_obj.create({
#                             'name': '%s to %s' % (partner.name, partner.dc_id.name,),
#                             'default_location_src_id': loc.id,
#                             'default_location_dest_id': loc_dc_quarantine_id,
#                             'sequence_id': seq_out.id,
#                             'warehouse_id': new_wh.id,
#                             'code' : 'internal'
#                         })
#                     if l == 'Transit':
#                         # CREATE OPERATION TRANSIT FROM DISTRIBUTION CENTER/SHOP (DC to SHOP)
#                         type_transit = type_obj.create({
#                             'name': 'Receipts from %s' % (DC.name,),
#                             'default_location_src_id': loc.id,
#                             'default_location_dest_id': stock_location.id,
#                             'sequence_id': seq_in.id,
#                             'warehouse_id': new_wh.id,
#                             'code': 'internal'
#                         })
#                         new_wh.in_type_id.write({
#                             'name': '%s to %s' % (partner.dc_id.name, partner.name,),
#                             'code': 'internal',
#                             'sequence_id': DC_Delivery.sequence_id.id,
#                             'warehouse_id': DC.id,
#                             # 'apply_mto': True,
#                             'default_location_src_id': DC_Delivery.default_location_src_id.id,
#                             'default_location_dest_id': loc.id
#                         })
#                         # PREPARE ROUTE AND PUSH RULES
#                         routes = self.env['stock.location.route']
#                         path = self.env['stock.location.path']
#                         routes_id = routes.search([('name' , '=', 'PTI ROUTES')], limit=1)
#                         if len(routes_id) == 0:
#                             res = routes.create({
#                                 'name': 'PTI ROUTES',
#                                 'active': True,
#                                 'warehouse_selectable': True
#                             })
#                             path.create({
#                                 'route_id': res.id,
#                                 'name': 'transit to %s' % (partner.name,),
#                                 'location_from_id': loc.id,
#                                 'location_dest_id': stock_location.id,
#                                 'picking_type_id': type_transit.id,
#                                 'active': True
#                             })
#                                
#                             partner.addWarehouse(res.id, new_wh.id)
#                             partner.addWarehouse(res.id, DC.id)
#                         else:
#                             exist = path.search([('location_from_id', '=', loc.id), ('location_dest_id', '=', stock_location.id)])
#                             if not exist.id:
#                                 path.create({
#                                        'route_id': routes_id.id,
#                                        'name': 'transit to %s' % (partner.name,),
#                                        'location_from_id': loc.id,
#                                        'location_dest_id': stock_location.id,
#                                        'picking_type_id': type_transit.id,
#                                        'active': True
#                                 })
#      
#                                 partner.addWarehouse(routes_id.id, new_wh.id)
#                          
#                   
#         return True

    def create_location_warehouse_dc(self, partner):
        if not partner.ref:
            raise UserError(_('Fill Internal Reference for DC first.(in Tab Sale & Purchases)'))
        wh_exist = self.env['stock.warehouse'].search(['|', ('name', '=', partner.name), ('code', '=', partner.ref or '-')])
        if wh_exist:
            return
        wh_vals = {
            'name' : partner.name,
            'code' : partner.ref,
            'dc_id' : partner.id,
            'partner_id' : partner.id
        }
        new_wh = self.env['stock.warehouse'].create(wh_vals)
        if len(new_wh) == 0:
            raise UserError(_("Ups, cannot create warehouse %s" % (partner.name)))
        ir_model_obj = self.pool['ir.model.data']
        type_obj = self.env['stock.picking.type']
        loc_obj = self.env['stock.location']
        seq_in = new_wh.in_type_id.sequence_id
        seq_out = new_wh.out_type_id.sequence_id
        view_location = new_wh.view_location_id
        stock_location = new_wh.lot_stock_id

        # RENAME VIEW LOCATION
        # for DC's warehouse, fill partner_id = dc_id
        view_location.write({
            'name': partner.name,
            'partner_id': partner.id,
            'dc_id': partner.id
        })

        # update stock location, fill partner_id = dc_id
        stock_location.write({
            'partner_id': partner.id,
            'dc_id': partner.id
        })                

        # GET INFORMATION NDC
        model, ndc_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'stock', 'warehouse0')
        NDC = self.env['stock.warehouse'].search([('id', '=', ndc_id)])
        NDC_Delivery = NDC.out_type_id

        model, customers_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'stock', 'stock_location_customers')
        model, ndc_transit_qua_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'pti_stock_default_mto', 'ndc_transit_quarantine')
        model, ndc_stag_loc_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'pti_stock_default_mto', 'ndc_staging')
        model, pick_tran_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'pti_stock_default_mto', 'picking_quarantine')
        model, ndc_quarantine_id = ir_model_obj.get_object_reference(self._cr, self._uid, 'pti_stock_default_mto', 'ndc_quarantine')

        for l in ['Transit', 'Quarantine', 'Bad Products']:
            loc = loc_obj.create({
                'name' : l,
                'location_id': view_location.id,
                'usage': 'internal',
                'active': True,
                'partner_id': partner.id,
                'dc_id': partner.id
            })
            if l == 'Quarantine':
                # CREATE OPERATION CUSTOMERS TO DISTRIBUTION CENTER
                type_customer = type_obj.create({
                    'name' : 'Customers to %s' % (partner.name,),
                    'default_location_src_id': customers_id,
                    'default_location_dest_id': loc.id,
                    'sequence_id': seq_in.id,
                    'warehouse_id': new_wh.id,
                    'code' : 'internal'
                })
                new_wh.out_type_id.write({
                    'return_picking_type_id': type_customer.id
                })
                # CREATE OPERATION DC TO NDC
                type_obj.create({
                    'name': '%s to NDC' % (partner.name,),
                    'default_location_src_id': loc.id,
                    'default_location_dest_id': ndc_transit_qua_id,
                    'sequence_id': seq_out.id,
                    'warehouse_id': new_wh.id,
                    'code' : 'internal'
                })
            if l == 'Transit':
                # CREATE OPERATION TRANSIT FROM DISTRIBUTION CENTER
                type_transit = type_obj.create({
                    'name': 'Receipts from %s' % (NDC.name,),
                    'default_location_src_id': loc.id,
                    'default_location_dest_id': stock_location.id,
                    'sequence_id': seq_in.id,
                    'warehouse_id': new_wh.id,
                    'code': 'internal'
                })
                new_wh.in_type_id.write({
                    'name': 'NDC to %s' % (partner.name,),
                    'code': 'internal',
                    'sequence_id': NDC_Delivery.sequence_id.id,
                    'warehouse_id': NDC.id,
                    'apply_mto': True,
                    'default_location_src_id': ndc_stag_loc_id,
                    'default_location_dest_id': loc.id
                })
                # PREPARE ROUTE AND PUSH RULES
                routes = self.env['stock.location.route']
                path = self.env['stock.location.path']
                routes_id = routes.search([('name' , '=', 'PTI ROUTES')], limit=1)
                if len(routes_id) == 0:
                    res = routes.create({
                        'name': 'PTI ROUTES',
                        'active': True,
                        'warehouse_selectable': True
                    })
                    path.create({
                        'route_id': res.id,
                        'name': 'transit to %s' % (partner.name,),
                        'location_from_id': loc.id,
                        'location_dest_id': stock_location.id,
                        'picking_type_id': type_transit.id,
                        'active': True
                    })
                    
                    partner.addWarehouse(res.id, new_wh.id)
                    partner.addWarehouse(res.id, NDC.id)
                else:
                    exist = path.search([('location_from_id', '=', loc.id), ('location_dest_id', '=', stock_location.id)])
                    if not exist.id:
                        path.create({
                            'route_id': routes_id.id,
                            'name': 'transit to %s' % (partner.name,),
                            'location_from_id': loc.id,
                            'location_dest_id': stock_location.id,
                            'picking_type_id': type_transit.id,
                            'active': True
                        })

                        partner.addWarehouse(routes_id.id, new_wh.id)

    def create_pos_config_by_shop_stand_alone(self, partner):
        if not partner.ref:
            raise UserError(_('Fill Internal Reference for SHOP first.(in Tab Sale & Purchases)'))
        if not partner.dc_id:
            raise UserError(_('Fill Distribution center and Category Shop for SHOP first.'))
        if not partner.category_shop:
            raise UserError(_('Fill Category Shop for SHOP first.'))

        config_obj = self.env['pos.config']
        # CREATE OPERATION POINT OF SALES
        pos_config = config_obj.create({
            'name': '%s' % (partner.name,),
            'category_shop': 'stand_alone',
            'cat_store_text': 'stand_alone',
        })
#         pos_config.write({'journal_ids': [(6, 0, self.getAccountJournals())], })
        return pos_config

    def create_pos_config_by_shop_in_shop(self, partner):
        if not partner.ref:
            raise UserError(_('Fill Internal Reference for SHOP first.(in Tab Sale & Purchases)'))
        if not partner.dc_id:
            raise UserError(_('Fill Distribution center and Category Shop for SHOP first.'))
        if not partner.category_shop:
            raise UserError(_('Fill Category Shop for SHOP first.'))
        if not partner.shop_identifier_origin:
            raise UserError(_('Fill Shop Identifier Origin for SHOP first.'))
        config_obj = self.env['pos.config']

        # CREATE OPERATION POINT OF SALES
        pos_config = config_obj.create({
            'name': '%s' % (partner.name,),
            'category_shop': 'shop_in_shop',
            'cat_store_text': 'shop_in_shop',
            'shop_identifier_origin': partner.shop_identifier_origin,
            'iface_print_auto': False,
            'cash_control': False,
            'iface_print_via_proxy': False,
            'iface_scan_via_proxy': True,
            'iface_cashdrawer': False,
        })
#         pos_config.write({'journal_ids': [(6, 0, self.getAccountJournals())], })
        return pos_config

    def create_pos_config_by_shop_mds(self, partner):
        if not partner.ref:
            raise UserError(_('Fill Internal Reference for SHOP first.(in Tab Sale & Purchases)'))
        if not partner.dc_id:
            raise UserError(_('Fill Distribution center and Category Shop for SHOP first.'))
        if not partner.category_shop:
            raise UserError(_('Fill Category Shop for SHOP first.'))
        if not partner.shop_identifier_origin:
            raise UserError(_('Fill Shop Identifier Origin for SHOP first.'))

        config_obj = self.env['pos.config']

        # CREATE OPERATION POINT OF SALES
        pos_config = config_obj.create({
            'name': '%s' % (partner.name,),
            'category_shop': 'shop_in_shop_mds',
            'cat_store_text': 'shop_in_shop_mds',
            'shop_identifier_origin': partner.shop_identifier_origin,
            'iface_print_auto': False,
            'cash_control': False,
            'iface_print_via_proxy': False,
            'iface_scan_via_proxy': True,
            'iface_cashdrawer': False,
        })
#         pos_config.write({'journal_ids': [(6, 0, self.getAccountJournals())], })
        return pos_config

    @api.multi
    def CreatePosConfigByShop(self):
        for partner in self:
            if partner.this_for_all:
                if partner.is_consignment or partner.is_team_leader:
                    raise UserError(_("Main company can't as consignment or TL."))
            elif partner.is_dc:
                self.create_location_warehouse_dc(partner)
            #####STAND ALONE#########
            elif partner.is_shop and partner.category_shop == 'stand_alone':
                return self.create_pos_config_by_shop_stand_alone(partner)
            #####SHOP IN SHOP########
            elif partner.is_shop and partner.category_shop == 'shop_in_shop':
                return self.create_pos_config_by_shop_in_shop(partner)
            #####SHOP IN SHOP MDS########
            elif partner.is_shop and partner.category_shop == 'shop_in_shop_mds':
                return self.create_pos_config_by_shop_mds(partner)
        return False
