odoo.define('pti_pos_free_product.loyalty_target_rewards_cheapest', function (require) {
 "use strict";

 var models = require('point_of_sale.models');

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
	 
	 apply_reward: function(reward){
		 var flag = false;
		 var lines = this.get_orderlines();
		 var line;
		 var products = [], target_lines = [];
		 if (reward.type === 'discount' && reward.is_cheapest_product){
			if(lines.length > 1){
				if(reward.is_for_all){
					target_lines = lines;
					flag = true;
				}else if(reward.discount_target_type == 'categories'){
					for (var i = 0; i < lines.length; i++) {
						line = lines[i];
						if (this.check_category(line.get_product().pos_category_ids, reward.discount_category_ids) == true){
							target_lines.push(line);
							flag = true;
						}
					}
				}else if(reward.discount_target_type == 'products'){
					for(var i = 0; i < lines.length; i++){
						line = lines[i]
						if(this.check_product(line.get_product().id, reward.discount_product_id) == true){
							target_lines.push(line);
							flag = true;
						}
					}
				}
				this.clear_discount()
				this.set_apply_discount(this.get_cheapest_products(target_lines), reward);
			}else{
				flag = true;
			}
		 }
		 if(flag === false){
			 return _super_posloyalty.prototype.apply_reward.apply(this, arguments)
		 }
	 },
	 
	 remove_orderline: function(line){
		 _super_posloyalty.prototype.remove_orderline.apply(this, arguments);
		 if(this.pos.config.loyalty_id != false){
             var rewards = this.get_available_rewards_automatic();
             var obj;
      	   /**********************************/
             if (rewards.length === 0) {
  	            return;
             }else if (rewards.length === 1) {
  	            //kalo daftar rewardsnya hanya ada satu
            	 if(rewards[0].select_manual == false){
	    	    	   	this.apply_reward(rewards[0]);
	    	        	this.loyalty_reward_id = rewards[0].id;
	    	        	this.reward = rewards[0];
 	        	}
 	            return;
             }
             /*********************************/
		 }
	 },
	 
	 clear_discount: function(){
		 var lines = this.get_orderlines();
		 for(var i=0; i<lines.length; i++){
			lines[i].discountStr = '0';
			lines[i].discount_base = 0;
			lines[i].trigger('change',lines[i]);
		 }
	 },
	 
	 get_cheapest_products: function(lines){
		 var lowest = Number.POSITIVE_INFINITY;
		 var tmp;
		 var line;
		 for (var i=lines.length-1; i>=0; i--) {
		     tmp = lines[i].get_product().list_price;
		     if (tmp < lowest){ 
		    	 lowest = tmp;
		    	 line = lines[i]
		     }
		 }
		 return line;
	 },
 });
})