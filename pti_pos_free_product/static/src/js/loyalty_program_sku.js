odoo.define('pti_pos_free_product.loyalty_program_sku', function (require) {
 "use strict";

 var models = require('point_of_sale.models');


 var _super_posorder = models.Order;
 models.Order = models.Order.extend({
	 initialize: function(attr,options) {
		 _super_posorder.prototype.initialize.apply(this,arguments);
		 this.SKU= "";
	 },
	 export_as_JSON: function(){
		var json = _super_posorder.prototype.export_as_JSON.apply(this,arguments);
		json.SKU = this.SKU;
		return json;
    },
    init_from_JSON: function(json){
    	_super_posorder.prototype.init_from_JSON.apply(this,arguments);
		this.SKU = json.SKU
    },
	
    add_product: function(product, options){
		_super_posorder.prototype.add_product.apply(this, arguments);
		this.set_loyalty_SKU()
	},
	
	remove_orderline: function(line){
		_super_posorder.prototype.remove_orderline.apply(this, arguments);
//		this.set_non_promo_SKU();
		this.SKU = "";
		this.pos_order_shop_identifier_period = "";
	},
	
	set_loyalty_SKU: function(){
		 if(this.pos.config.loyalty_id != false){
			 var rewards = this.get_available_rewards_automatic();
		     var reward, rule;
		     
		     reward = rewards[0];
		     
		     if(reward){
			     rule = this.get_rule_from_reward(reward)
			     this.SKU = rule.shop_identifier_promo_period
			     this.pos_order_shop_identifier_period = rule.shop_identifier_promo_period
		     }
//		     }else{
//		    	 this.SKU = this.get_sk_prod()
//		    	 this.set_non_promo_SKU();
//		     }
		 }
	 },
	
	set_non_promo_SKU: function(){
		if(this.pos.config.shop_identifier_promo_period){
			this.SKU = this.pos.config.shop_identifier_promo_period
			this.pos_order_shop_identifier_period = this.pos.config.shop_identifier_promo_period
		}else{
			this.SKU = this.pos.config.shop_identifier_origin
		}
	}
 });
})