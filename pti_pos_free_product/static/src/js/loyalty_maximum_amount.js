odoo.define('pti_pos_free_product.loyalty_maximum_amount', function (require) {
 "use strict";

 var utils = require('web.utils');
 
 var models = require('point_of_sale.models');
 var round_pr = utils.round_precision;
 
 var _super_posmodel = models.PosModel.prototype;
 models.PosModel = models.PosModel.extend({
     initialize: function (session, attributes) {
         var partner_model = _.find(this.models, function(model){ return model.model === 'loyalty.reward'; });
         partner_model.fields.push('max_reward');
         partner_model.fields.push('max_reward_value');
         return _super_posmodel.initialize.call(this, session, attributes);
     },
 });
 
 var _super_posloyalty = models.Order;
 models.Order = models.Order.extend({
	//get_discount_text: function(show_discount){
	initialize: function(attr,options) {
		_super_posloyalty.prototype.initialize.apply(this,arguments);
		this.is_max_reward = false;
		this.max_reward_value = 0;
		this.discount_max_reward = 0;
		this.maximum_reward = 0;
	},
	export_as_JSON: function(){
		var json = _super_posloyalty.prototype.export_as_JSON.apply(this,arguments);
		json.is_max_reward = this.is_max_reward;
		json.max_reward_value = this.max_reward_value;
		json.discount_max_reward = this.discount_max_reward;
		json.maximum_reward = this.maximum_reward;
		return json;
    },
    init_from_JSON: function(json){
		_super_posloyalty.prototype.init_from_JSON.apply(this,arguments);
		this.is_max_reward = json.is_max_reward;
		this.max_reward_value = json.max_reward_value;
		this.discount_max_reward = json.discount_max_reward;
		this.maximum_reward = json.maximum_reward;
    },
	 
    check_maximum_reward: function(max_reward){
		return max_reward;
	},
	 
	set_maximum_reward: function(total_purchase, max_reward_value, reward){
		var total_purchase_with_discount = 0;
		if(total_purchase > max_reward_value){
			this.clear_discount();
			total_purchase_with_discount = ((reward.discount) / 100) * max_reward_value;
			this.is_max_reward = true;
			this.discount_max_reward = reward.discount;
			this.maximum_reward = reward.max_reward_value;
		}
		return total_purchase_with_discount;
	 },
	 
	 apply_reward: function(reward){
		 _super_posloyalty.prototype.apply_reward.apply(this, arguments)
		 var total_purchase = this.get_total_discount() + this.get_grand_total() + this.max_reward_value;
		 this.max_reward_value = 0;
		 this.is_max_reward = false;
		 if (reward.type === 'discount' && this.check_maximum_reward(reward.max_reward) === true){
			 this.max_reward_value = this.set_maximum_reward(total_purchase, reward.max_reward_value, reward);
			 this.trigger('change', this);
		 }
	 },

	 get_total_discount: function() {
		 return round_pr(this.orderlines.reduce((function(sum, orderLine) {
	            return sum + (orderLine.get_unit_price() * (orderLine.discount_base/100) * orderLine.get_quantity());
		 }), 0), this.pos.currency.rounding);
	 },
	 
	 get_grand_total: function(){
		 var total = _super_posloyalty.prototype.get_grand_total.apply(this, arguments)
		 if(this.is_max_reward){
			 total = total - this.max_reward_value
		 }
		 return total;
	 },
	 
	 remove_orderline: function(line){
		 _super_posloyalty.prototype.remove_orderline.apply(this, arguments);
		 this.is_max_reward = false;
		 this.max_reward_value = 0;
	 },
	 
 });
})