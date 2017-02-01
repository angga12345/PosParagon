odoo.define('pos_loyalty.pos_loyalty', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var utils = require('web.utils');

var round_di = utils.round_decimals;
var round_pr = utils.round_precision;
var QWeb     = core.qweb;
var _t = core._t;


models.load_fields('res.partner','loyalty_points');

models.load_models([
    {
        model: 'loyalty.program',
        condition: function(self){ return !!self.config.loyalty_id[0]; },
        fields: ['name','pp_currency','pp_product','pp_order','rounding','start_date','end_date','term_condition_text'],
        domain: function(self){ return [['id','=',self.config.loyalty_id[0]]]; },
        loaded: function(self,loyalties){ 
            self.loyalty = loyalties[0];
        },
    },{
        model: 'loyalty.reward',
        condition: function(self){ return !!self.loyalty; },
        fields: ['name',
                 'type',
                 'minimum_points',
                 'gift_product_id',
                 'point_cost',
                 'discount_product_id',
                 'discount',
                 'point_value',
                 'point_product_id',
                 'rule_id',
                 'is_multilevel_discount',
                 'is_cheapest_product',
                 'is_for_all',
                 'discount_multilevel_id',
                 'flag',
                 'select_manual',
                 'display_term'],
        domain: function(self){ return [['loyalty_program_id','=',self.loyalty.id]]; },
        loaded: function(self,rewards){
            console.log('Loyalty id',self.loyalty.id)
            self.loyalty.rewards = rewards;
            self.set({'loyaltyreward':rewards})
            ////////console.log('Rewards Set : ', self.loyalty.rewards);
            self.loyalty.rewards_by_id = {};
            for (var i = 0; i < rewards.length;i++) {
                self.loyalty.rewards_by_id[rewards[i].id] = rewards[i];
            }
        },
    },{
        model: 'loyalty.multi.level.discount',
        condition: function(self){ return !!self.loyalty; },
        fields: ['name','quantity','discount_product_id','discount','reward_id'],
        loaded: function(self, multi_level_discount){
            self.loyalty.multi_level_discount = multi_level_discount;
        },
    },{
        model: 'loyalty.target.product.line',
        condition: function(self){ return !!self.loyalty; },
        fields: ['product_id','rule_id',],
        loaded: function(self, target_product_line){
            self.loyalty.target_product_line = target_product_line;
        },
    },{
        model: 'loyalty.rule',
        condition: function(self){ return !!self.loyalty; },
        fields: ['name',
                 'type',
                 'product_id',
                 'product_ids',
                 'category_ids',
                 'cumulative',
                 'qty_rule',
                 'price_rule',
                 'pp_product',
                 'pp_currency',
                 'is_different_product',
                 'for_all_products',
                 'produk_pwp_ids',
                 'shop_identifier_promo_period',
                 'sku_number_period'
                 ],
        domain: function(self){ return [['loyalty_program_id','=',self.loyalty.id]]; },
        loaded: function(self,rules){ 

            self.loyalty.rules = rules;
            self.set({'loyaltyrule':rules})
            ////////console.log('Rules : ', rules);
            // not used anymore cause product & category in rule it change from m2o to m2m
            // self.loyalty.rules_by_product_id = {};
            // self.loyalty.rules_by_category_id = {};
        },
    },
],{'after': 'product.product'});

var _super_orderline = models.Orderline;
models.Orderline = models.Orderline.extend({
    get_reward: function(){
        if(this.pos.loyalty){
            return this.pos.loyalty.rewards_by_id[this.reward_id];
        }
    },
    // This is how to extend a function from class Orderline
    // To change the calculation of price based on Rule for Discount Series
    get_display_price: function(){
        var res = _super_orderline.prototype.get_display_price.apply(this);
        if('got_reward' in this){
            ////////console.log('Line : ', this);
            var reward = this.got_reward;
            var trigger_rules = reward.triggerby_active_rules;
            if(trigger_rules && trigger_rules.length){
                for (var obj in trigger_rules){
                    var rule = trigger_rules[obj];
                    // discount series 
                    if(rule.is_different_product && this.get_quantity() > rule.qty_rule){
                        var rounding = this.pos.currency.rounding;
                        var disc_value = round_pr(this.get_unit_price() * rule.qty_rule, rounding) * (this.discount_base/100);
                        var price = round_pr(this.get_unit_price() * this.get_quantity(), rounding);
                        var final_price = price - disc_value;
                        return final_price;
                    }
                }
            }
        }
        return res;
    },
    set_reward: function(reward){
        this.reward_id = reward.id;
    },
    export_as_JSON: function(){
        var json = _super_orderline.prototype.export_as_JSON.apply(this,arguments);
        json.reward_id = this.reward_id;
        return json;
    },
    init_from_JSON: function(json){
        _super_orderline.prototype.init_from_JSON.apply(this,arguments);
        this.reward_id = json.reward_id;
    },
});

var _super = models.Order;
models.Order = models.Order.extend({

    /* Get the rule when activated in order */
    get_rules_active_id: function(){
        var orderLines = this.get_orderlines();
        var rules_active_id = [];
        var categories_selected_list = [];
        var products_selected_list = [];
        ////console.log('HALO~HALO', this.pos.db.product_by_id)
        
        
        for (var i = 0; i < orderLines.length; i++) {
            var line = orderLines[i];
            var product = line.get_product();
            var list_product = [product.id];
            var rules = this.pos.loyalty.rules;
            

            if(list_product){
                for (var obj in rules){
                    var rule = rules[obj];
                    
                    if(rules[obj].for_all_products == true){
                        ////console.log('One Two Three',rules[obj].produk_pwp_ids)
                        var product_selected = line.check_contains_all(list_product, rules[obj].produk_pwp_ids);    
                        if(product_selected.state && product_selected.data){
                            if(line.get_quantity() >= rule.qty_rule && line.get_price_with_tax() >= rule.price_rule){
                                products_selected_list.push(product_selected.data);
                                var uniqueprod = [];
                                $.each(products_selected_list, function(i, el){
                                    if($.inArray(el, uniqueprod) === -1) uniqueprod.push(el);
                                });
                                rules_active_id.push({
                                    'active_id': rule.id,
                                    'qty_rule': rule.qty_rule,
                                    'qty_order': line.get_quantity(),
                                    'price_rule': rule.price_rule,
                                    'pp_product': rule.pp_product,
                                    'count_product': rule.produk_pwp_ids.length,
                                    'count_category': rule.category_ids.length,
                                    'product_selected': uniqueprod,
                                    'category_selected': categories_selected_list,
                                    'product_id': line.get_product().id,
                                    'produk_pwp_ids': rule.produk_pwp_ids,
                                    'is_different_product': rule.is_different_product,
                                    'use_hour_rules': rule.use_hour_rules,
                                    'type': rule.type,
                                    'applied': rule.applied,
                                    'product_ids': rule.product_ids,
                                    'category_ids': rule.category_ids,
                                })
                            }
                        }
                    }else{
                        var product_selected = line.check_contains_all(list_product, rules[obj].product_ids);
                        if(product_selected.state && product_selected.data){
                            if(line.get_quantity() >= rule.qty_rule && line.get_price_with_tax() >= rule.price_rule){
                            	products_selected_list.push(product_selected.data);
                                var uniqueprod = [];
                                $.each(products_selected_list, function(i, el){
                                    if($.inArray(el, uniqueprod) === -1) uniqueprod.push(el);
                                });
                                rules_active_id.push({
                                    'active_id': rule.id,
                                    'qty_rule': rule.qty_rule,
                                    'qty_order': line.get_quantity(),
                                    'price_rule': rule.price_rule,
                                    'pp_product': rule.pp_product,
                                    'count_product': rule.product_ids.length,
                                    'count_category': rule.category_ids.length,
                                    'product_selected': uniqueprod,
                                    'category_selected': categories_selected_list,
                                    'product_id': line.get_product().id,
                                    'product_ids': rule.product_ids,
                                    'is_different_product': rule.is_different_product,
                                    'use_hour_rules': rule.use_hour_rules,
                                    'type': rule.type,
                                    'applied': rule.applied,
                                    'product_ids': rule.product_ids,
                                    'category_ids': rule.category_ids,
                                })
                            }
                        }
                    }
                }
            }

//            var rules  = this.pos.loyalty.rules_by_product_id[product.id] || [];
//            var overriden = false;

            if (line.get_reward()) {  // Reward products are ignored
                continue;
            }
 
            // Test the category rules
            if (product.pos_category_ids && product.pos_category_ids.length) {
                ////console.log('categ ids',product, product.category_ids)
                for (var obj in rules){
                    var categories_selected = line.check_contains_all(product.pos_category_ids, rules[obj].category_ids);
                    ////console.log('categories selected',rules[obj].category_ids)
                    if(categories_selected.state && categories_selected.data){
                        var rule = rules[obj];
                        categories_selected_list.push(categories_selected.data);
                        var uniquecateg = [];
                        $.each(categories_selected_list, function(i, el){
                            if($.inArray(el, uniquecateg) === -1) uniquecateg.push(el);
                        });
                        rules_active_id.push({
                            'active_id': rule.id,
                            'qty_rule': rule.qty_rule,
                            'qty_order': line.get_quantity(),
                            'price_rule': rule.price_rule,
                            'pp_product': rule.pp_product,
                            'count_product': rule.product_ids.length,
                            'count_category': rule.category_ids.length,
                            'product_selected': products_selected_list,
                            'category_selected': uniquecateg,
                            'product_id': line.get_product().id,
                            'is_different_product': rule.is_different_product,
                            'use_hour_rules': rule.use_hour_rules,
                            'type': rule.type,
                            'applied': rule.applied,
                            'product_ids': rule.product_ids,
                            'category_ids': rule.category_ids,
                        })
                    }
                }
            }
        }
        ////console.log('Active Rules : ', rules_active_id);
        return rules_active_id;
    },

    /* The total of points won, excluding the points spent on rewards */
    get_won_points: function(){
        if (!this.pos.loyalty) {
            return 0;
        }
        
        var orderLines = this.get_orderlines();
        var rounding   = this.pos.loyalty.rounding;
        
        var product_sold = 0;
        var total_sold   = 0;
        var total_points = 0;

        for (var i = 0; i < orderLines.length; i++) {
            var line = orderLines[i];
            var product = line.get_product();
            var list_product = [product.id];
            var rules = this.pos.loyalty.rules;

            var overriden = false;

            if(list_product){
                for (var obj in rules){
                    var rule = rules[obj];
                    var product_selected = line.check_contains_all(list_product, rules[obj].product_ids);
                    if(product_selected.state && product_selected.data){
                        if(line.get_quantity() >= rule.qty_rule || line.get_price_with_tax() >= rule.price_rule){
                            total_points += round_pr(line.get_quantity() * rule.pp_product, rounding);
                            total_points += round_pr(line.get_price_with_tax() * rule.pp_currency, rounding);
                            if (!rule.cumulative) { 
                                overriden = true;
                                break;
                            }
                        }
                    }
                }
            }

            // Test the category rules
            if (product.pos_category_ids && product.pos_category_ids.length) {
                var rules = this.pos.loyalty.rules;
                for (var obj in rules){
                    var categories_selected = line.containsAll(product.pos_category_ids, rules[obj].category_ids);
                    if(categories_selected){
                        var rule = rules[obj];
                        total_points += round_pr(line.get_quantity() * rule.pp_product, rounding);
                        total_points += round_pr(line.get_price_with_tax() * rule.pp_currency, rounding);
                        if (!rule.cumulative) {
                            overriden = true;
                            break;
                        }
                    }
                }
            }

            if (!overriden) {
                product_sold += line.get_quantity();
                total_sold   += line.get_price_with_tax();
            }
        }

        total_points += round_pr( total_sold * this.pos.loyalty.pp_currency, rounding );
        total_points += round_pr( product_sold * this.pos.loyalty.pp_product, rounding );
        total_points += round_pr( this.pos.loyalty.pp_order, rounding );

        return total_points;
    },

    /* The total number of points spent on rewards */
    get_spent_points: function() {
        if (!this.pos.loyalty) {
            return 0;
        } else {
            var lines    = this.get_orderlines();
            var rounding = this.pos.loyalty.rounding;
            var points   = 0;

            for (var i = 0; i < lines.length; i++) {
                var line = lines[i];
                var reward = line.get_reward();
                if (reward) {
                    if (reward.type === 'gift') {
                        points += round_pr(line.get_quantity() * reward.point_cost, rounding);
                    } else if (reward.type === 'discount') {
                        // points += round_pr(-line.get_display_price() * reward.point_cost, rounding);
                        //points += round_pr(line.get_quantity() * reward.point_cost, rounding);
                        points = round_pr(this.get_won_points(), rounding)
                        // untuk PWP
                        if (line.get_product().id == reward.discount_product_id[0]){
                            var disc_value = line.get_display_price() * (reward.discount/100);
                            line.discountStr = '' + reward.discount;
                            line.discount_base = reward.discount;
                            
                        }
                    } else if (reward.type === 'resale') {
                        points += (-line.get_quantity());
                    }
                }
            }

            return points;
        }
    },

    /* The total number of points lost or won after the order is validated */
    get_new_points: function() {
        if (!this.pos.loyalty) {
            return 0;
        } else { 
            return round_pr(this.get_won_points() - this.get_spent_points(), this.pos.loyalty.rounding);
        }
    },

    /* The total number of points that the customer will have after this order is validated */
    get_new_total_points: function() {
        if (!this.pos.loyalty) {
            return 0;
        } else { 
            //return round_pr(this.get_client().loyalty_points + this.get_new_points(), this.pos.loyalty.rounding);
            return round_pr(this.get_new_points(), this.pos.loyalty.rounding);
        }
    },

    /* The number of loyalty points currently owned by the customer */
    get_current_points: function(){
        return this.get_client() ? this.get_client().loyalty_points : 0;
    },

    /* The total number of points spendable on rewards */
    get_spendable_points: function(){
        if (!this.pos.loyalty) {
            return 0;
        } else {
            return round_pr(this.get_new_points(), this.pos.loyalty.rounding);
//            return round_pr(this.get_client().loyalty_points - this.get_spent_points(), this.pos.loyalty.rounding);
        }
    },
    containReward: function(values, list){
      if($.inArray(values, list) != -1) return true;
      
      return false;
    },
    get_available_rewards_automatic: function(){
        var lol  = this.pos.get_order();
        
        var rewards = [];
        var qty_rule = 0;
        for (var i = 0; i < this.pos.loyalty.rewards.length; i++) {
            var orderrr = this.pos.pos_order_now;
            var reward = this.pos.loyalty.rewards[i];
            var active_rules = this.get_rules_active_id();
            console.log('aktif rules',active_rules)
            //////console.log('Flag Orderrr: ',orderrr.flag)
            ////console.log('OK OK',this.pos.get_order_list())
            var daftar_order = this.pos.get_order_list();
            ////console.log('Panjang daftar order: ',daftar_order.length)
            
            
            
            
            if (reward.minimum_points > this.get_spendable_points()) {
                continue;
            } else if(reward.type === 'gift' && reward.point_cost > this.get_spendable_points()) {
                continue;
            } else if(reward.type === 'resale' && this.get_spendable_points() <= 0) {
                continue;
            } else if(reward.type === 'discount' && reward.point_cost > this.get_spendable_points()) {
                continue;
            }
            
            //////////console.log('point yang dihabiskan: ',this.get_spendable_points())
            var products = [];
            for (var flag=0; flag < daftar_order.length;flag++){
                //jika get order name sama dengan daftar order name pas waktu diklik (+) difront-end
                if(lol.name == daftar_order[flag].name){
                    ////console.log('AHA',daftar_order[flag].name,daftar_order[flag].flag)
                    var flag_order= daftar_order[flag].flag;
                    ////console.log('Flag Order: ',flag_order,active_rules)
                    
                    
                    if(active_rules.length){
                        for(var obj in active_rules){
                            var rule = active_rules[obj];
                            //console.log('^V^',rule,reward)
                            if(reward.type == 'discount'){
                                if(!reward.is_multilevel_discount && !reward.is_for_all){
                                    if(rule.count_category > 0 && rule.category_selected.length  == rule.count_category){
                                        if(rule.qty_order >= rule.qty_rule && reward.rule_id[0] == rule.active_id && !reward.is_cheapest_product){
                                            ////console.log('discount,qty order > qty rule')
                                            reward['triggerby_active_rules'] = active_rules;
                                            rewards.push(reward);
                                            break;
                                        }
                                        else if(reward.rule_id[0] == rule.active_id && reward.is_cheapest_product){
                                            ////console.log('discount cheapest product')
                                            reward['triggerby_active_rules'] = active_rules;
                                            rewards.push(reward);
                                            break;
                                        }
                                    }
                                    // untuk PWP
                                    if(!rule.is_different_product){
                                        if(rule.count_product > 0){
                                            //////console.log('Count Product: ',rule.count_product)
                                            //////console.log('Price Rule: ',rule.price_rule)
                                            //jika total order lebih dari price rule => masuk sini
                                            if(reward.rule_id[0] == rule.active_id){
                                                //console.log('reward rule id sama dengan rule active id: ',reward.rule_id[0],rule.active_id)
                                            	rewards.push(reward);
                                                //console.log('rewards: ',rewards)
                                                break;
                                            }
                                        }
                                    }
                                    // untuk Discount Series
                                    else{
                                        if(rule.count_product > 0 && rule.product_selected.length == rule.count_product){
                                            if(rule.qty_order >= rule.qty_rule && reward.rule_id[0] == rule.active_id){
                                                reward['triggerby_active_rules'] = active_rules;
                                                rewards.push(reward);
                                                break;
                                            }
                                        }
                                    }
                                }
                            }
                            //daftar order sesuai dengan id | Gift || resale
                            if(rule.product_selected.length == rule.count_product){
                                //jika point yang dihabiskan sm dengan cost point
                                if((reward.type === 'gift' || reward.type === 'resale') && this.get_spendable_points() >= reward.point_cost && reward.rule_id[0] == rule.active_id){
                                	var v = this.containReward(reward.id, lol.bendera_ids);
                                    ////console.log(v)
                                    ////console.log('sebelum',lol.bendera_ids)
                                    if(v == false){
                                        rewards.push(reward);
                                    }
                                    lol.bendera_ids.push(reward.id) 
                                    ////console.log('sesudah',lol.bendera_ids)
                                    break;
                                } 
                            }
//                            if(rule.category_selected.length  == rule.count_category){
//                                if((reward.type === 'gift' || reward.type === 'resale') && this.get_spendable_points() >= reward.point_cost && reward.rule_id[0] == rule.active_id){
//                                    alert('pppppppppp')
//                                	var v = this.containReward(reward.id, lol.bendera_ids);
//                                    ////console.log(v)
//                                    ////console.log('sebelum',lol.bendera_ids)
//                                    if(v == false){
//                                        rewards.push(reward);
//                                    }
//                                    lol.bendera_ids.push(reward.id) 
//                                    ////console.log('sesudah',lol.bendera_ids)
//                                    break;
//                                } 
//                            }
                            
                        }
                        if(!reward.rule_id && (reward.type === 'gift' || reward.type === 'resale')){
                            rewards.push(reward);
                        }
                    }else{
                        if(!reward.rule_id && (reward.type === 'gift' || reward.type === 'resale')){
                            rewards.push(reward);
                        }
                        if(reward.type == 'discount' && !reward.is_multilevel_discount && reward.is_for_all){
                            rewards.push(reward);
                        }
//                        else{
//                            var lines = this.get_orderlines();
//                            for(var obj in lines){
//                                var line = lines[obj];
//                                var multilevels = this.get_multi_level_discount(reward);
//                                for (var level in multilevels){
//                                    var disc_product = multilevels[level].discount_product_id[0];
//                                    if(line.get_product().id == disc_product){
//                                        rewards.push(reward);
//                                        break;
//                                    }
//                                    break;
//                                }
//                                break;
//                            }
//                        }
                    }
                    //
                }//tutup kondisi 
                
            }//tutup perulangan daftar semua order pada front-end       
        }
        return rewards;
    },

    /* The list of rewards that the current customer can get */
    get_available_rewards: function(){
        var rewards = [];
        var qty_rule = 0;
        for (var i = 0; i < this.pos.loyalty.rewards.length; i++) {
            var reward = this.pos.loyalty.rewards[i];
            var active_rules = this.get_rules_active_id();
            if (reward.minimum_points > this.get_spendable_points()) {
                continue;
            } else if(reward.type === 'gift' && reward.point_cost > this.get_spendable_points()) {
                continue;
            } else if(reward.type === 'resale' && this.get_spendable_points() <= 0) {
                continue;
            }

            var products = [];
            if(active_rules.length){
                for(var obj in active_rules){
                    var rule = active_rules[obj];
                    if(rule.product_selected.length == rule.count_product){
                        if((reward.type === 'gift' || reward.type === 'resale') && rule.qty_order >= rule.qty_rule && reward.rule_id[0] == rule.active_id){
                            rewards.push(reward);
                            break;
                        } 
                    }
                    if(rule.category_selected.length  == rule.count_category){
                        if((reward.type === 'gift' || reward.type === 'resale') && rule.qty_order >= rule.qty_rule && reward.rule_id[0] == rule.active_id){
                            rewards.push(reward);
                            break;
                        } 
                    }
                }
                if(!reward.rule_id && (reward.type === 'gift' || reward.type === 'resale')){
                    rewards.push(reward);
                }
            }else{
                if(!reward.rule_id && (reward.type === 'gift' || reward.type === 'resale')){
                    rewards.push(reward);
                }
            }
        }
        return rewards;
    },
    
    get_2nd_available_rewards: function(){
        var rewards = [];
        for (var i = 0; i < this.pos.loyalty.rewards.length; i++) {
            var reward = this.pos.loyalty.rewards[i];
            var active_rules = this.get_rules_active_id();
            if (reward.minimum_points > this.get_spendable_points()) {
                continue;
            } else if(reward.type === 'discount' && reward.point_cost > this.get_spendable_points()) {
                continue;
            }
            if(reward.type === 'discount'){
                if(!reward.is_multilevel_discount && !reward.is_for_all){
                    var categories = [];
                    for(var obj in active_rules){
                        var rule = active_rules[obj];
                        if(rule.count_category > 0 && rule.category_selected.length  == rule.count_category){
                            if(rule.qty_order >= rule.qty_rule && reward.rule_id[0] == rule.active_id){
                                reward['triggerby_active_rules'] = active_rules;
                                rewards.push(reward);
                                break;
                            }
                        }
                        ////////console.log('Rule Product : ', rule.product_selected)
                        // untuk PWP
                        if(!rule.is_different_product){
                            if(rule.count_product > 0){
                                if(rule.qty_order >= rule.qty_rule && reward.rule_id[0] == rule.active_id){
                                    rewards.push(reward);
                                    break;
                                }
                            }
                        }
                        // untuk Discount Series
                        else{
                            if(rule.count_product > 0 && rule.product_selected.length == rule.count_product){
                                if(rule.qty_order >= rule.qty_rule && reward.rule_id[0] == rule.active_id){
                                    reward['triggerby_active_rules'] = active_rules;
                                    rewards.push(reward);
                                    break;
                                }
                            }
                        }
                    }
                }
                else if(!reward.is_multilevel_discount && reward.is_for_all){
                    ////////console.log('Reward For All : ', reward);
                    rewards.push(reward);
                }
                else{
                    var lines = this.get_orderlines();
                    for(var obj in lines){
                        var line = lines[obj];
                        ////////console.log('Reward : ', reward);
                        var multilevels = this.get_multi_level_discount(reward);
                        for (var level in multilevels){
                            var disc_product = multilevels[level].discount_product_id[0];
                            if(line.get_product().id == disc_product){
                                rewards.push(reward);
                                break;
                            }
                            break;
                        }
                        break;
                    }
                }   
            }
        }
        return rewards;
    },

    get_multi_level_discount: function(reward){
        ////////console.log('Multi Level :', this.pos.loyalty.multi_level_discount);
        var multi_level_disc = this.pos.loyalty.multi_level_discount || [];
        var multi_level_by_reward_id = [];
        for (var i = 0; i < multi_level_disc.length; i++) {
            var disc_multilevel = multi_level_disc[i];
            if (disc_multilevel.reward_id[0] == reward.id){
                multi_level_by_reward_id.push(disc_multilevel);
            }
        }
        return multi_level_by_reward_id;
    },

    get_target_product_line: function(rules){
        var target_product_line_obj = this.pos.loyalty.target_product_line || [];
        for (var i = 0; i < target_product_line_obj.length; i++){
            var target_product_line = target_product_line_obj[i];
            for (var obj in rules.target_product_line){
                if(target_product_line.id == rules.target_product_line[obj]){
                    return target_product_line;
                }
            }
        }
    },

    has_discount: function(){
        var discount = false
        var reward;
        this.orderlines.each(function(line){
            reward = line.get_reward();
            if (reward && reward.type === 'discount') {
                discount = true;
            }
        });
        return discount;        
    },

    get_discount_from_reward: function(){
        var crounding   = this.pos.currency.rounding;
        var order_total = this.get_total_with_tax();
        var multilevels = this.pos.loyalty && this.pos.loyalty.multi_level_discount;
        var lines       = this.orderlines;
        var discount    = 0;
        var reward;
        return Math.round(lines.reduce((function(sum, line){
            reward = line.get_reward();
            if (reward && reward.type === 'discount') {
                if(!reward.is_multilevel_discount && reward.is_for_all){
                    console.log('discount for reward',order_total,reward.discount,line.get_price_disc())
                    discount = sum + round_pr(line.get_price_disc()*-1,crounding)
                    // discount = (sum + round_pr(order_total, crounding)) * (reward.discount/100);
                }
                else{
                    var discount_multi_level_id;
                    for (var obj in multilevels){
                        var multilevel = multilevels[obj];
                        if(multilevel.reward_id[0] == reward.id){
                            for(var obj in lines.models){
                                var orderline = lines.models[obj];
                                if(orderline.get_quantity() >= multilevel.quantity && orderline.get_product().id == multilevel.discount_product_id[0]){
                                    discount_multi_level_id = multilevel;
                                    // line.product.list_price = -discount;
                                    break;
                                }
                            }
                        }
                    }
                    if(discount_multi_level_id){
                        var disc_product = discount_multi_level_id.discount_product_id[0];
                        for (var obj in lines.models){
                            var orderline = lines.models[obj];
                            if(orderline.get_product().id == disc_product){
                                order_total = sum + orderline.get_display_price();
                                discount = sum + round_pr(order_total * (discount_multi_level_id.discount/100), crounding);
                                // line.product.list_price = -discount;
                                // break;
                            }
                        }   
                    }else{
                    	discount = sum + round_pr(line.get_price_disc()*-1,crounding)
                    }
                }
            }
            return discount;
        }), 0));
    },

    get_line_discount: function(){
        var multilevels = this.pos.loyalty.multi_level_discount;
        var lines       = this.orderlines;
        var reward, get_line;
        lines.each(function(line){
            reward = line.get_reward();
            if (reward && reward.type === 'discount') {
                if(!reward.is_multilevel_discount){
                    get_line = line;
                }
                else{
                    var discount_multi_level_id;
                    for (var obj in multilevels){
                        var multilevel = multilevels[obj];
                        if(multilevel.reward_id[0] == reward.id){
                            for(var obj in lines.models){
                                var orderline = lines.models[obj];
                                if(orderline.get_quantity() >= multilevel.quantity && orderline.get_product().id == multilevel.discount_product_id[0]){
                                    discount_multi_level_id = multilevel;
                                    // line.product.list_price = -discount;
                                    break;
                                }
                            }
                        }
                    }
                    if(discount_multi_level_id){
                        var disc_product = discount_multi_level_id.discount_product_id[0];
                        for (var obj in lines.models){
                            var orderline = lines.models[obj];
                            if(orderline.get_product().id == disc_product){
                                get_line = line;
                                // line.product.list_price = -discount;
                                // break;
                            }
                        }   
                    }
                }
            }
        });
        return get_line;
    },

    apply_reward: function(reward){
        var client = this.get_client();
        var product, order_total, spendable;
        var lrounding, crounding;
        
        if (reward.type === 'gift') {
            product = this.pos.db.get_product_by_id(reward.gift_product_id[0]);
            if (!product) {
                return;
            }

            this.add_product(product, { 
                price: 0, 
                quantity: 1, 
                merge: false, 
                extras: { reward_id: reward.id },
            });
        } else if (reward.type === 'discount') {
            if(reward.is_multilevel_discount){
                var product = this.pos.db.get_product_by_id(reward.discount_product_id[0]);

                if(!product){
                    return;
                }

                var display_name = product.display_name
                product.display_name = display_name + ' - ' + reward.name;

                this.add_product(product, {
                    quantity: 1, 
                    merge: false,
                    extras: { reward_id: reward.id },
                });
            }
            else if(!reward.is_multilevel_discount && reward.is_for_all){
                var lines = this.get_orderlines();
                for (var i = 0; i < lines.length; i++) {
                    var line = lines[i];
                    if (reward.discount > line.discount_base){
                        line.discountStr = '' + reward.discount;
                        line.discount_base = reward.discount;   
                    }
                    this.select_orderline(line);
                }

            }
            else{
                var lines = this.get_orderlines();
                var total = 0
                for (var i = 0; i < lines.length; i++) {
                    var line = lines[i];
                    if (reward.triggerby_active_rules){
                        for (var obj in reward.triggerby_active_rules){
                            var rule = reward.triggerby_active_rules[obj];
                            //////console.log('rule rule',rule)
                            if (rule.count_product > 0 && rule.product_selected.length == rule.count_product){
                                for (var ps in rule.product_selected){
                                    var product = rule.product_selected[ps];
                                    if(line.get_product().id == product){
                                        var disc_value = line.get_display_price() * (reward.discount/100);
                                        line.discountStr = '' + reward.discount;
                                        line.discount_base = reward.discount;
                                        line['got_reward'] = reward;
                                        this.select_orderline(line);    
                                    }
                                }
                            }
                        }
                    }else{
                        var tot_tax = this.get_total_tax();
                        var active_rules = this.get_rules_active_id();
                        var ln_product_id = line.get_product().id;
                        var ln_product = line.get_product();
                        //////console.log('get product',line)
                        for (var a in active_rules){
                            if(active_rules[a].price_rule > 0){
                                //console.log('Price rule: ',active_rules[a])
                                if(active_rules[a].produk_pwp_ids){
                                    //active rules produk pwp ids
                                    for (var b in active_rules[a].produk_pwp_ids){
                                        var list_prod_pwp = active_rules[a].produk_pwp_ids[b];
                                        if(ln_product_id == list_prod_pwp){
                                            //////console.log('produk pwp')
                                            //////console.log('produk',ln_product)
                                            var ln_prc = ln_product.price * line.quantity;
                                            console.log('lol',ln_prc, total)
                                            total = total + ln_prc;
                                            break;
                                        }
                                        
                                    }
                                }else{
                                    //active rules product ids
                                    for (var b in active_rules[a].product_ids){
                                        var list_prod_pwp = active_rules[a].product_ids[b];
                                        if(ln_product_id == list_prod_pwp){
                                            //////console.log('produk pwp')
                                            //////console.log('produk',ln_product)
                                            var ln_prc = ln_product.price * line.quantity;
                                            console.log('lol',ln_prc, total)
                                            total = total + ln_prc;
                                            break;
                                        }
                                        
                                    }
                                }
                                
                                
                            break;  
                            }
                        }
                        
                        //console.log('Total sekarang: ',total)
                        // untuk PWP
                        if (total > active_rules[a].price_rule){
                            /*Menambahkan Product Discount DiAwal,DiTengah*/
                            for(var line_prod in lines){
                                if(lines[line_prod].product.id == reward.discount_product_id[0]){
                                    //adjustment amount of products
                                    var disc_value = lines[line_prod].price * (reward.discount/100);
                                    lines[line_prod].discountStr = '' + reward.discount;
                                    lines[line_prod].discount_base = reward.discount;
                                    this.select_orderline(lines[line_prod]); // menyisipkan langsung diskon ke produk
                                    
                                }
                                
                            }
                            /**/
                            /*menambahkan Product Discount DiAkhir*/
                            if (line.get_product().id == reward.discount_product_id[0]){
                                //adjustment amount of products
                                var disc_value = line.get_display_price() * (reward.discount/100);
                                line.discountStr = '' + reward.discount;
                                line.discount_base = reward.discount;
                                //console.log('len len',line)
                            }
                            /**/
                            this.select_orderline(line); // menyisipkan langsung diskon ke produk
                            
                        }
                        
                    }
                }
            }

        } else if (reward.type === 'resale') {
            lrounding = this.pos.loyalty.rounding;
            crounding = this.pos.currency.rounding;
            spendable = this.get_spendable_points();
            order_total = this.get_total_with_tax();
            product = this.pos.db.get_product_by_id(reward.point_product_id[0]);

            if (!product) {
                return;
            }

            if ( round_pr( spendable * product.price, crounding ) > order_total ) {
                spendable = round_pr( Math.floor(order_total / product.price), lrounding);
            }

            if ( spendable < 0.00001 ) {
                return;
            }

            this.add_product(product, {
                quantity: -spendable,
                merge: false,
                extras: { reward_id: reward.id },
            });
        }
    },

    get_grand_total : function(){
        if(this.get_membership_disc()!= null ){
            return round_pr((this.get_total_with_tax() - this.get_member_disc_value()) + this.get_voucher_price(), this.pos.currency.rounding);
        }
        else{
//            return round_pr(this.get_total_with_tax() + this.get_voucher_price() - this.get_discount_from_reward(), this.pos.currency.rounding);
        	return round_pr(this.get_total_with_tax() + this.get_voucher_price(), this.pos.currency.rounding);
        }
    },

    get_due: function(paymentline) {
        if (!paymentline) {
            var due = this.get_grand_total() - this.get_total_paid();
        } else {
            var due = this.get_grand_total();
            
            var lines = this.paymentlines.models;
            for (var i = 0; i < lines.length; i++) {
                if (lines[i] === paymentline) {
                    break;
                } else {
                    due -= lines[i].get_amount();
                    
                }
            }
        }
        return round_pr(Math.max(0,due), this.pos.currency.rounding);
    },

    get_change: function(paymentline) {
        if (!paymentline) {
            var change = this.get_total_paid() - this.get_grand_total();
        } else {
            var change = -this.get_grand_total(); 
            var lines  = this.paymentlines.models;
            for (var i = 0; i < lines.length; i++) {
                change += lines[i].get_amount();
                if (lines[i] === paymentline) {
                    break;
                }
            }
        }
        return round_pr(Math.max(0,change), this.pos.currency.rounding);
    },

    finalize: function(){
        var client = this.get_client();
        if ( client ) {
            client.loyalty_points = this.get_new_total_points();
            // The client list screen has a cache to avoid re-rendering
            // the client lines, and so the point updates may not be visible ...
            // We need a better GUI framework !
            this.pos.gui.screen_instances.clientlist.partner_cache.clear_node(client.id);
        }
        _super.prototype.finalize.apply(this,arguments);
    },

    export_for_printing: function(){
        var json = _super.prototype.export_for_printing.apply(this,arguments);
        if (this.pos.loyalty && this.get_client()) {
            json.loyalty = {
                rounding:     this.pos.loyalty.rounding || 1,
                name:         this.pos.loyalty.name,
                client:       this.get_client().name,
                points_won  : this.get_won_points(),
                points_spent: this.get_spent_points(),
                points_total: this.get_new_total_points(), 
            };
        }
        return json;
    },

    export_as_JSON: function(){
        var json = _super.prototype.export_as_JSON.apply(this,arguments);
        json.loyalty_points = this.get_new_points();
        return json;
    },
});

var LoyaltyButton = screens.ActionButtonWidget.extend({
    template: 'LoyaltyButton',
//    button_click: function(){
//        var order  = this.pos.get_order();
//        var rewards = order.get_available_rewards_automatic();
//     
//            //menampilkan daftar rewards 
//        if(rewards.length > 0){
//	        var list = [];
//	        var reward, product;
//	        for (var i = 0; i < rewards.length; i++){
//	        	reward = rewards[0]
//	        	if(reward.type == 'gift'){
//		            for (var i = 0; i < reward.discount_product_id.length; i++) {
//		                product = this.pos.db.get_product_by_id(reward.discount_product_id[i])
//		                list.push({
//		                    label: product.display_name,
//		                    item: product,
//		                });
//		            }
//	        	}
//	        }
//	        this.gui.show_popup('selection',{
//	            'title': 'Please select a reward',
//	            'list': list,
//	            'confirm': function(product){
//	            	order.add_product(product, {discount: 100,
//	                  merge: false});
//	            },
//	        });
//        }
//    },
    button_click: function(){
        var order  = this.pos.get_order();
        var rewards = order.get_available_rewards_automatic();
        var aktif = order.get_rules_active_id();
        
        if (rewards.length === 0) {
            this.gui.show_popup('alert',{
                'title': 'No Rewards Available',
                'body':  'There are no rewards available for this customer as part of the loyalty program',
            });
            return;
        } else if (rewards.length === 1 && this.pos.loyalty.rewards.length === 1) {
            //kalo daftar rewardsnya hanya ada satu
            if (order.get_spent_points() > 0){
                this.gui.show_popup('alert',{
                    'title': 'MAAF REWARDS HANYA DAPAT DIGUNAKAN SEKALI',
                    'body':  'MAAF ANDA SUDAH MENGGUNAKAN REWARDS ANDA...',
                });
                return;
            }else{
                order.apply_reward(rewards[0]);
                order.loyalty_reward_id = rewards[0].id;
	        	order.reward = rewards[0];
            }
            return;
        } else {
            //menampilkan daftar rewards 
            var list = [];
            for (var i = 0; i < rewards.length; i++) {
            	if(rewards[i].select_manual){
	                list.push({
	                    label: rewards[i].name,
	                    item:  rewards[i],
	                });
            	}
            }
            this.gui.show_popup('selection',{
                'title': 'Please select a reward',
                'list': list,
                'confirm': function(reward){
                    var item_order_ln;
                    // mengecek rule active id dari orderline
                    for (var i = 0; i < aktif.length; i++) {
                        // mengecek kalo reward yang ada didaftar bila sama dengan rule aktif id dalam orderline
                        // dan reward yg ada didaftar mempunyai bendera
                        for(var obj in list){
                            if(list[obj].item.rule_id[0] == aktif[i].active_id && list[obj].item.flag){
                                item_order_ln = list[obj].item;
                            }
                        }   
                    }
                    

                    if (order.get_spent_points() > 0 && reward.rule_id[0] == item_order_ln.rule_id[0] && item_order_ln.flag){
                        alert('MAAF REWARDS HANYA DAPAT DIGUNAKAN SEKALI');
                        return;
                    }else{
                        order.apply_reward(reward);
                        order.loyalty_reward_id = rewards[0].id;
	    	        	order.reward = rewards[0];
                        //untuk mengetahui bahwa item sudah pernah dipakai
                        reward.flag = true
                    }
                },
            });
        }
    },
});

var LoyaltySecondOrderButton = screens.ActionButtonWidget.extend({
    template: 'LoyaltySecondOrderButton',
    button_click: function(){
        var order  = this.pos.get_order();
        var rewards = order.get_2nd_available_rewards();
        ////////console.log('... >>> ...',rewards)
        if (rewards.length === 0) {
            this.gui.show_popup('alert',{
                'title': 'No Rewards Available',
                'body':  'There are no rewards available for this customer as part of the loyalty program',
            });
            return;
        } else if (rewards.length === 1 && this.pos.loyalty.rewards.length === 1) {
            order.apply_reward(rewards[0]);
            return;
        } else { 
            var list = [];
            for (var i = 0; i < rewards.length; i++) {
                list.push({
                    label: rewards[i].name,
                    item:  rewards[i],
                });
            }
            this.gui.show_popup('selection',{
                'title': 'Please select a reward',
                'list': list,
                'confirm': function(reward){
                    order.apply_reward(reward);
                },
            });
        }
    },
});

screens.define_action_button({
    'name': 'loyalty',
    'widget': LoyaltyButton,
    'condition': function(){
    	return this.pos.loyalty && this.pos.loyalty.rewards.length;
    },
});

screens.define_action_button({
    'name': 'giftproducts',
    'widget': LoyaltySecondOrderButton,
    'condition': function(){
        return this.pos.loyalty && this.pos.loyalty.rewards.length;
    },
});

screens.OrderWidget.include({
    update_summary: function(){
        this._super();

        var order = this.pos.get_order();

        var $loypoints = $(this.el).find('.summary .loyalty-points');
        // disini tempatnya u/ menampilkan Points
        if(this.pos.loyalty){
            var points_won      = order.get_won_points();
            var points_spent    = order.get_spent_points();
            var points_total    = order.get_new_total_points();

            var has_discount    = order.has_discount();
            var lines           = order.get_line_discount() || false;
            var total           = order ? order.get_special_price() : 0;
            var selected        = order ? order.get_selected_orderline() : 0;

//            if(has_discount && lines){
//                var discount  = order.get_discount_from_reward();
//                lines.node.childNodes[3].innerText = this.format_currency(-discount);
//                this.el.querySelector('#discount').textContent = this.format_currency(discount);
//                this.el.querySelector('.summary .total > .value').textContent = this.format_currency(total);
//            }

            $loypoints.replaceWith($(QWeb.render('LoyaltyPoints',{ 
                widget: this, 
                rounding: this.pos.loyalty.rounding,
                points_won: points_won,
                points_spent: points_spent,
                points_total: points_total,
            })));
            $loypoints = $(this.el).find('.summary .loyalty-points');
            $loypoints.removeClass('oe_hidden');

            if(points_total < 0){
                $loypoints.addClass('negative');
            }else{
                $loypoints.removeClass('negative');
            }
        }else{
            $loypoints.empty();
            $loypoints.addClass('oe_hidden');
        }

        if (this.pos.loyalty &&
            this.getParent().action_buttons &&
            this.getParent().action_buttons.loyalty) {

            var rewards = order.get_available_rewards_automatic();
            if(rewards && (!order.reward)){
	            for(var i=0; i<rewards.length; i++){
	            	if(rewards[i].select_manual){
	            		this.getParent().action_buttons.loyalty.highlight(true);
	            	}else{
	            		this.getParent().action_buttons.loyalty.highlight(false);
	            	}
	            }
            }else{
            	this.getParent().action_buttons.loyalty.highlight(false);
            }
        }
    },
});

});