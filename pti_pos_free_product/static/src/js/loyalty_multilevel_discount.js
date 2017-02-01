odoo.define('pti_pos_free_product.loyalty_multilevel_discount', function (require) {
 "use strict";

 var models = require('point_of_sale.models');

 var _super_posmodel = models.PosModel.prototype;
 models.PosModel = models.PosModel.extend({
	 initialize: function (session, attributes) {
         var partner_model = _.find(this.models, function(model){ return model.model === 'loyalty.multi.level.discount'; });
         partner_model.fields.push('discount_product_ids');
         partner_model.fields.push('discount_category_ids');
         return _super_posmodel.initialize.call(this, session, attributes);
     },
 });

 var _super_posloyalty = models.Order;
 models.Order = models.Order.extend({
	check_product_qty: function(qty_product, qty_target){
		if(qty_product == qty_target) return true;
		return false;
	},

	get_available_rewards_automatic: function(){
		var lines = this.get_orderlines();
		var rule;
		var active_rules = this.get_rules_active_id();
		if(_super_posloyalty.prototype.get_available_rewards_automatic.apply(this, arguments)){
            for (var i = 0; i < active_rules.length; i++){
                rule = active_rules[i];
                if(rule.type === 'product'){
                    for (var i = 0; i < lines.length; i++) {
                        var line = lines[i];
                        if(this.check_product(line.get_product().id, rule.product_ids) == true && line.get_quantity() >= rule.qty_rule){
                            return this.get_rewards(rule);
                        }
                    }
                }else if(rule.type === 'category'){
                    for (var i = 0; i < lines.length; i++) {
                        var line = lines[i];
                        if (this.check_category(line.get_product().pos_category_ids, rule.category_ids) == true && this.get_category_qty(line.get_product().pos_category_ids) >= rule.qty_rule){
                            return this.get_rewards(rule);
                        }
                    }
                }
            }
		}
		return _super_posloyalty.prototype.get_available_rewards_automatic.apply(this, arguments)
	},

	get_rewards: function(rule){
		var rewards = [];
		var reward;
		for (var i = 0; i < this.pos.loyalty.rewards.length; i++){
			reward = this.pos.loyalty.rewards[i]
			if(rule.active_id == reward.rule_id[0]){
				rewards.push(reward);
			}
		}
		return rewards;
	},

	check_multilevel_discount: function(reward){
		if (reward.is_multilevel_discount){
			return true;
		}
		return false;
	},
 
	apply_reward: function(reward){
		var flag = false;
		var lines = this.get_orderlines();
		console.log(reward)
		if (this.check_multilevel_discount(reward)){
			for (var i = 0; i < lines.length; i++) {
				var line = lines[i];
				this.set_multilevel_discount_reward(line);
			}
			flag = true;
		}

		if(flag === false){
			return _super_posloyalty.prototype.apply_reward.apply(this, arguments);
		}
	},

	check_qty_products: function(discount_category_ids){
		var total = 0;
		var lines = this.get_orderlines();
		for (var i = 0; i < lines.length; i++) {
			var line = lines[i];
			if(this.check_category(line.get_product().pos_category_ids, discount_category_ids)){
				total = total + line.get_quantity()
			}
		}
		return total
	},
	
	set_multilevel_discount_reward: function(line){
		var multilevel_discount;
		var total_qty = 0;
		for(var i=0; i < this.pos.loyalty.multi_level_discount.length; i++){
			multilevel_discount = this.pos.loyalty.multi_level_discount[i];
			total_qty = this.check_qty_products(multilevel_discount.discount_category_ids)
			if(this.check_product(line.get_product().id, multilevel_discount.discount_product_ids) === true){
				if(this.check_product_qty(line.get_quantity(), multilevel_discount.quantity)){
					this.set_apply_multilevel_discount(line, multilevel_discount);
				}
			}else if(this.check_category(line.get_product().pos_category_ids, multilevel_discount.discount_category_ids) === true){
	 			if(this.check_product_qty(total_qty, multilevel_discount.quantity)){
	 				this.set_apply_multilevel_discount(line, multilevel_discount);
	 			}
			}
		}
		return multilevel_discount;
	},
	
	set_apply_multilevel_discount: function(line, discount_value){
		line.discountStr = '' + discount_value.discount;
		line.discount_base = discount_value.discount;
		line.trigger('change',line);
	}
 });
})