odoo.define('pti_pos_free_product.loyalty_target_rewards', function (require) {
 "use strict";

 var models = require('point_of_sale.models');

 var _super_posmodel = models.PosModel.prototype;
 models.PosModel = models.PosModel.extend({
     initialize: function (session, attributes) {
         var partner_model = _.find(this.models, function(model){ return model.model === 'loyalty.reward'; });
         partner_model.fields.push('discount_target_type');
         partner_model.fields.push('discount_category_ids');
         return _super_posmodel.initialize.call(this, session, attributes);
     },
 });

 var _super_posloyalty = models.Order;
 models.Order = models.Order.extend({
	 check_category: function(product_category_ids, target_category_id){
			for(var i = 0 , len = product_category_ids.length; i < len; i++){
				if($.inArray(product_category_ids[i], target_category_id) != -1){
					return true;
				}
			}
			return false;
	 },
		
	 check_product: function(product_id, product_ids){
		if($.inArray(product_id, product_ids) != -1) return true;
	      return false;
	 },

	get_available_rewards_automatic: function(){
		var rewards = _super_posloyalty.prototype.get_available_rewards_automatic.apply(this, arguments) || [];
		for (var i = 0; i < this.pos.loyalty.rewards.length; i++) {
            var reward = this.pos.loyalty.rewards[i];
            if(reward.is_for_all){
            	rewards.push(reward)
            }
		}
		return rewards;
	},
	 
	 apply_reward: function(reward){
		 var flag = false;
		 var lines = this.get_orderlines();
		 if (reward.type === 'discount'){
			 if (reward.discount_target_type === 'products'){
				for (var i = 0; i < lines.length; i++) {
					var line = lines[i];
					if (this.check_product(line.get_product().id, reward.discount_product_id) == true){
						this.set_apply_discount(line, reward);
						flag = true;
					}
				}
			 }else if (reward.discount_target_type === 'categories'){
				for (var i = 0; i < lines.length; i++) {
					var line = lines[i];
					if (this.check_category(line.get_product().pos_category_ids, reward.discount_category_ids) == true){
						this.set_apply_discount(line, reward);
						flag = true;
					}
				}
		     }
		 }else if(reward.type === 'gift'){
			 if(reward.is_cheapest_product === false){
				 this.set_apply_reward(reward);
				 flag = true;
			 }
		 }
	     
		 if(flag === false){
			 return _super_posloyalty.prototype.apply_reward.apply(this, arguments)
		 }
	 },
	 
	 set_apply_discount: function(line, discount_value){
		line.discountStr = '' + discount_value.discount;
		line.discount_base = discount_value.discount;
		line.trigger('change',line);
	 },
	 
	 set_apply_reward: function(reward){
		 var product;
		 for(var i=0;i<reward.gift_product_id.length;i++){
			 product = this.pos.db.get_product_by_id(reward.gift_product_id[i]);
//			 if(this.check_gift_product_exist(product.id) == false){
				this.add_product(product, { 
		             price: 0, 
		             quantity: 1, 
		             discount: 100,
		             merge: false, 
		             extras: { reward_id: reward.id }
				 });
//			 }
		 }
	},
	
	check_gift_product_exist: function(product_id){
		var lines = this.get_orderlines();
		var line;
		for(var i=0; i<lines.length; i++){
			line = lines[i];
			if(product_id == line.get_product().id){
				return true;
			}
		}
		return false;
	},
 });
})