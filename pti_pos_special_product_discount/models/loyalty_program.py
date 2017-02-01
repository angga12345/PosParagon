from openerp import models, fields, api, _


type_shop = [('global', 'Global'),
             ('stand_alone', 'Stand Alone'),
             ('shop_in_shop', 'Shop in Shop'),
             ('shop_in_shop_mds', 'Shop in Shop MDS')]


class LoyaltyProgram(models.Model):
    _inherit = "loyalty.program"

    name = fields.Char(string='Programs Name')
    is_all = fields.Boolean(string='Applied For All Shop', default=False)
    applied_on = fields.Selection(string='Applied On', selection=type_shop)
    start_date = fields.Date(string='Start Date', required=1)
    end_date = fields.Date(string='End Date', required=1)
    term_condition_text = fields.Text(string="Terms and Conditions")

    # for many2many
    def _set_loyalty_program_ids(self, domain, loyalty_program_id):
        lp_ids = {'loyalty_program_ids': [(4, loyalty_program_id)]}
        return self.env['pos.config'].search(domain).write(lp_ids)

    def _remove_loyalty_program_ids(self, loyalty_program_id):
        lp_ids = {'loyalty_program_ids': [(3, loyalty_program_id)]}
        return self.env['pos.config'].search([]).write(lp_ids)

    def _update_loyalty_program_ids(self, domain, loyalty_program_id):
        self._remove_loyalty_program_ids(loyalty_program_id)
        return self._set_loyalty_program_ids(domain, loyalty_program_id)

    # for many2one
    def _set_loyalty_program_id(self, domain, loyalty_program_id):
        lp_id = {'loyalty_id': loyalty_program_id}
        return self.env['pos.config'].search(domain).write(lp_id)

    def _remove_loyalty_program_id(self, domain, loyalty_program_id):
        configs = self.env['pos.config'].search(domain)
        for config in configs:
            config.write({'loyalty_id': False})

    def _update_loyalty_program_id(self, domain, loyalty_program_id):
        self._remove_loyalty_program_id([('loyalty_id', '=', loyalty_program_id)], loyalty_program_id)
        return self._set_loyalty_program_id(domain, loyalty_program_id)

    @api.model
    def create(self, values):
        lp_id = super(LoyaltyProgram, self).create(values)
        if lp_id and lp_id.applied_on:
            if lp_id.applied_on == 'global':
                self._set_loyalty_program_id([], lp_id.id)
            elif lp_id.applied_on == 'stand_alone':
                domain = [('category_shop', '=', 'stand_alone')]
                self._set_loyalty_program_id(domain, lp_id.id)
            elif lp_id.applied_on == 'shop_in_shop':
                domain = [('category_shop', '=', 'shop_in_shop')]
                self._set_loyalty_program_id(domain, lp_id.id)
            else:
                domain = [('category_shop', '=', 'shop_in_shop_mds')]
                self._set_loyalty_program_id(domain, lp_id.id)
        return lp_id

    @api.multi
    def write(self, values):
        lp_ip_update = super(LoyaltyProgram, self).write(values)
        if not self.is_all or not self.applied_on:
            self._remove_loyalty_program_id([('loyalty_id', '=', self.id)],
                                            self.id)
        else:
            if self.applied_on == 'global':
                self._update_loyalty_program_id([], self.id)
            elif self.applied_on == 'stand_alone':
                standalone = [('category_shop', '=', 'stand_alone')]
                self._update_loyalty_program_id(standalone, self.id)
            elif self.applied_on == 'shop_in_shop':
                shop_in_shop = [('category_shop', '=', 'shop_in_shop')]
                self._update_loyalty_program_id(shop_in_shop, self.id)
            else:
                mds = [('category_shop', '=', 'shop_in_shop_mds')]
                self._update_loyalty_program_id(mds, self.id)
        return lp_ip_update


class LoyaltyReward(models.Model):
    _inherit = "loyalty.reward"
    
    discount_desc = fields.Text(string="Discount Description")
    discount_pti = fields.Float(string='Discount PTI')
    discount_mds = fields.Float(string='Discount MDS')
    type = fields.Selection([('gift', 'Gift'),
                             ('discount', 'Discount'),
                             ('resale', 'Resale'),
                             ('special_price','Special Price'),
                             ('next_purchase','Next Purchase')],
                             string = 'Type', required=True, help='The type of the reward')
    special_price = fields.Float('Special Price')
    max_reward = fields.Boolean(string='Maximum Reward')
    max_reward_value = fields.Float(string='Maximum Reward Value')
    discount_text = fields.Text(string="Discount Text")
    select_manual = fields.Boolean(string="Is Selected Manually")
    display_term = fields.Boolean(string="Display Term Condition")
#     @api.multi
#     def _get_default_domain_for_rules_ids(self):
#         loyalty_program_id = self.env.context.get('loyalty_program_id')
#         return [('loyalty_program_id', '=', loyalty_program_id)]

    rule_id = fields.Many2one('loyalty.rule', string='Rule')
#     rule_ids = fields.Many2many('loyalty.rule', string='Rules',
#                                 domain=_get_default_domain_for_rules_ids)
    is_multilevel_discount = fields.Boolean(string='Multilevel Discount')
    is_for_all = fields.Boolean(string='For All in Orders',
                                default=False,
                                help='Make the discount will apply for all products in orders')
    discount_multilevel_id = fields.One2many('loyalty.multi.level.discount',
                                             'reward_id',
                                             string='Discount Multilevel')
    flag = fields.Boolean(string='Flag')
    discount_product_id = fields.Many2many('product.product',
                                            string='Discount Product')
#     discount_category_ids = fields.Many2many('product.category',
#                                              string="Discount Product Category")
    discount_category_ids = fields.Many2many('pos.product.category',
                                             string="Discount Product Category")
    discount_target_type = fields.Selection([('products', 'Products'),
                                            ('categories', 'Categories')],
                                            string="Target Discount",
                                            default='products')
    is_cheapest_product = fields.Boolean(string='Cheapest Product')

    @api.onchange('discount_pti', 'discount_mds')
    def onchange_discount(self):
        self.discount = self.discount_pti + self.discount_mds

    @api.model
    def create(self, values):
        values['discount'] = values['discount_pti'] + values['discount_mds']
        lr_id_create = super(LoyaltyReward, self).create(values)
        if lr_id_create:
            print 'WOI KESINI DONG PLEASE' #wkwkwk, semangat bro !!!
            #jika price rule pwp
            rid = values.get('rule_id')
            prod_id = values.get('discount_product_id')
            if rid:
                print 'rule id',rid
                lt_prg_data = self.env['loyalty.rule'].browse(rid)
                simpan = []
                print lt_prg_data.for_all_products
                if lt_prg_data.for_all_products:
                    for listofpwpproduct in lt_prg_data.produk_pwp_ids:
                        simpan.append(listofpwpproduct.id)
                         
                    print 'Data',simpan
             
                    for a in simpan:
                        if a == prod_id:
                            print 'Cetak sini',a
                            simpan.remove(a);
                            #print "List : ", simpan
                             
                            print "List : ", simpan
                            #menghapus id produk yg ada pada produk pwp ids yg sm dengan id produk product discount dari reward
                            for ubah in lt_prg_data:
                                ubah.write({'produk_pwp_ids': [(6,0,[simpan])] })
                                print 'Ubah',ubah
            
        return lr_id_create
    
    @api.multi
    def write(self, values):
        for rec in self:
            values['discount'] = values.get('discount_pti', rec.discount_pti) + values.get('discount_mds', rec.discount_mds)
        lr_ip_update = super(LoyaltyReward, self).write(values)
        #jika price rule pwp
        if self.rule_id.price_rule:
            print 'rule id',self.rule_id.id
            print 'Reward Product: ',values.get('discount_product_id')
            
        prod_id = values.get('discount_product_id')
        
        lt_prg_id = self.env['loyalty.rule'].search([('id', '=', self.rule_id.id)]).id
        lt_prg_data = self.env['loyalty.rule'].browse(lt_prg_id)
        simpan = []
        if lt_prg_data.for_all_products:
            for listofpwpproduct in lt_prg_data.produk_pwp_ids:
                simpan.append(listofpwpproduct.id)
                
            print 'Data',simpan
            
            for a in simpan:
                if a == prod_id:
                    print 'Cetak sini',a
                    simpan.remove(a);
                    #print "List : ", simpan
                    
                    print "List : ", simpan
                    #menghapus id produk yg ada pada produk pwp ids yg sm dengan id produk product discount dari reward
                    for ubah in lt_prg_data:
                        ubah.write({'produk_pwp_ids': [(6,0,[simpan])] })
                        print 'Ubah',ubah
            
        return lr_ip_update

    @api.onchange('is_for_all')
    def onchange_is_for_all(self):
        if not self.is_for_all:
            self.discount_product_id = None
#       since the discount_product_id change into many2many field, this code produce bug
#         else:
#             product_tmpl_id = self.env.ref('pti_pos_special_product_discount.product_discount_coupon').id
#             product_id = self.env['product.product'].search([('product_tmpl_id', '=', product_tmpl_id)]).id
#             self.discount_product_id = product_id

    def _check_discount_product(self, cr, uid, ids, context=None):
        for reward in self.browse(cr, uid, ids, context=context):
            if reward.type == 'discount':
                return True
            else:
                return True

    _constraints = [
        (_check_discount_product, "The discount product field is mandatory for discount rewards", ["type","discount_product_id"]),
    ]


class LoyaltyRule(models.Model):
    _inherit = "loyalty.rule"

    @api.onchange('for_all_products')
    def _onchange_for_all_products(self):
        #fill produk_pwp_ids Automatically after fill Price rule 
        cr = self.pool.cursor()
        self.env
        #print 'TEST',self.pool.get('product.template').search(cr, self.env.uid, [])
        if self.for_all_products == True:
            self.produk_pwp_ids = self.pool.get('product.product').search(cr, self.env.uid, [])
            print '-_-',self.produk_pwp_ids
        else:
            self.produk_pwp_ids = False

    is_different_product = fields.Boolean(string='Different Product')
    category_id = fields.Many2one('pos.product.category',
                                  string='Target Categories',
                                  help='The categories affected by the rule')
    category_ids = fields.Many2many('pos.product.category',
                                    string='Target Categories',
                                    help='The categories affected by the rule')
    product_ids = fields.Many2many('product.product',
                                   string='Target Products',
                                   help='The products affected by the rule')
    qty_rule = fields.Float(string='Quantity Rule',
                            help='How many quantity are set for the rule')
    price_rule = fields.Float(string='Price Rule',
                              help='How many price are set for the rule')
    for_all_products = fields.Boolean(string='For All Products',
                                default=False,
                                help='for empty target products')
    shop_identifier_promo_period = fields.Char('Shop Identifier Period')
    sku_number_period = fields.Char(string='SKU Number Period', readonly=True)


class LoyaltyTargetProductLine(models.Model):
    _name = "loyalty.target.product.line"
    _description = 'Loyalty Target Product Line'

    product_id = fields.Many2one('product.product',
                                 string='Target Product',
                                 help='The product affected by the rule')

    rule_id = fields.Many2one('loyalty.rule', string='Rule')


class LoyaltyMultiLevelDiscount(models.Model):
    _name = "loyalty.multi.level.discount"
    _description = 'Loyalty Multi Level Discount'

    name = fields.Char(string='Level')
    quantity = fields.Float(string='Quantity', help='Quantity in cumulative')
    discount = fields.Float(string='Discount', help='The discount percentage')
    discount_product_ids = fields.Many2many('product.product',
                                            string='Discount Product')
    discount_category_ids = fields.Many2many('pos.product.category',
                                             string='Discount Categories')
    reward_id = fields.Many2one('loyalty.reward', string='Reward')
