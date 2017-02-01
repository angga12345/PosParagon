odoo.define('pti_pos_free_product.loyalty_target_rules', function (require) {
 "use strict";

 var models = require('point_of_sale.models');
 
 function checkIfEqual(arr1, arr2) {
	 if (arr1.length != arr2.length) {
		 return false;
	 }
	 //sort them first, then join them and just compare the strings
	 return arr1.sort().join() == arr2.sort().join();
 }
 
 var _super_posmodel = models.PosModel.prototype;
 models.PosModel = models.PosModel.extend({
     initialize: function (session, attributes) {
         var partner_model = _.find(this.models, function(model){ return model.model === 'loyalty.rule'; });
         partner_model.fields.push('applied');
         return _super_posmodel.initialize.call(this, session, attributes);
     },
 });
 
 var _super_loyalty = models.Order;
 models.Order = models.Order.extend({ 
	 check_all_products: function(products, product_ids){
		return checkIfEqual(products, product_ids);
	 },

	 check_array: function(value, values){
		 for(var i=0; i<values.length; i++){
			 if(value == values[i]){
				 return true;
			 }
		 }
		 return false;
	 },
	 
	 check_all_categories: function(categories, category_ids){
		 var rule_category;
		 for(var i=0; i < category_ids.length; i++){
			 rule_category = category_ids[i]
			 if(categories != '' && this.check_array(rule_category, categories.split(',')) === false){
				 return false
			 }
		 }
		return true
	 },
	 
	 get_all_products: function(is_categories){
		 var products = [];
		 var lines = this.get_orderlines();
		 var line;
//		 TODO: NEED TO OTHER ALGORITHM
		 for(var i=0; i<lines.length; i++){
			 line = lines[i];
			 if(is_categories === true){
				 if(!line.check_special_price()){
					 products = products + ',' + line.get_product().pos_category_ids
				 }
			 }else{
				 if(!line.check_special_price()){
					 products.push(line.get_product().id)
				 }
			 }
		 }
		 return products;
	 },

	 get_rules_active_id: function(){
		var rules = _super_loyalty.prototype.get_rules_active_id.apply(this, arguments);
		var active_rules = this.pos.loyalty.rules;
		for (var obj in active_rules){
            var rule = active_rules[obj];
            if(rule.type == 'all' && this.get_grand_total() >= rule.price_rule){
            	rules.push({
                    'active_id': rule.id,
                    'qty_rule': rule.qty_rule,
//                    'qty_order': line.get_quantity(),
                    'price_rule': rule.price_rule,
                    'pp_product': rule.pp_product,
                    'count_product': rule.product_ids.length,
                    'count_category': rule.category_ids.length,
                    'product_selected': [],
                    'category_selected': [],
//                    'product_id': line.get_product().id,
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
		return rules;
	},
	 
	get_available_rewards_automatic: function(){
		var active_rules = this.get_rules_active_id();
		var products = this.get_all_products(false);
		var categories = this.get_all_products(true);
		var rule, reward, flag=false;
		var rewards = [];
		for (var j = 0; j < this.pos.loyalty.rewards.length; j++){
			reward = this.pos.loyalty.rewards[j];
			for (var i = 0; i < active_rules.length; i++){
				
				rule = active_rules[i];
				if(rule.type === 'all'){
					rewards.push(reward)
					flag = true;
//					return rewards;
				}else{
					if(rule.applied === 'all'){
						if((this.check_all_products(products, rule.product_ids) && rule.type == 'product') || 
								(this.check_all_categories(categories, rule.category_ids) && rule.type == 'category')){
							return _super_loyalty.prototype.get_available_rewards_automatic.apply(this, arguments);
						}
					}else if(rule.applied === 'one'){
						return _super_loyalty.prototype.get_available_rewards_automatic.apply(this, arguments);
					}
				}
			}
		}

		if(flag == true){
			return rewards;
		}else{
			return false;
		}
	},
 });
})