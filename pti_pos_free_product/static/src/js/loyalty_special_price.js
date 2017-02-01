odoo.define('pti_pos_free_product.loyalty_special_price', function (require) {
 "use strict";

 var models = require('point_of_sale.models');
 var screens = require('point_of_sale.screens');
 
 var _super_posmodel = models.PosModel.prototype;
 models.PosModel = models.PosModel.extend({
     initialize: function (session, attributes) {
         var partner_model = _.find(this.models, function(model){ return model.model === 'loyalty.reward'; });
         partner_model.fields.push('special_price');
         return _super_posmodel.initialize.call(this, session, attributes);
     },
 });
 
 var _super_orderline = models.Orderline;
 models.Orderline = models.Orderline.extend({
	initialize: function(attr,options) {
		_super_orderline.prototype.initialize.apply(this,arguments);
		this.is_special_price = false;
		this.index_special_price;
	},
	export_as_JSON: function(){
		var json = _super_orderline.prototype.export_as_JSON.apply(this,arguments);
		json.is_special_price = this.is_special_price;
		json.index_special_price = this.index_special_price;
		return json;
    },
    init_from_JSON: function(json){
		_super_orderline.prototype.init_from_JSON.apply(this,arguments);
		this.is_special_price = json.is_special_price;
		this.index_special_price = json.index_special_price;
    },
    
    check_special_price: function(){
    	return this.is_special_price;
    },
    can_be_merged_with: function(orderline){
    	if(this.check_special_price()){
    		return false;
    	}
    	return _super_orderline.prototype.can_be_merged_with.apply(this,arguments);
    },
    
//	get_quantity: function(){
//		if(this.check_special_price()){
//			return this.quantity;
//		}
//	 },
 });
 
 var _super_posloyalty = models.Order;
 models.Order = models.Order.extend({
	 initialize: function(attr,options) {
        _super_posloyalty.prototype.initialize.apply(this,arguments);
        this.special_price = 0;
        this.index_special_price_order = 1;
	 },
	 export_as_JSON: function(){
		var json = _super_posloyalty.prototype.export_as_JSON.apply(this,arguments);
		json.special_price = this.special_price;
		json.index_special_price_order = this.index_special_price_order;
		return json;
    },
    init_from_JSON: function(json){
		_super_posloyalty.prototype.init_from_JSON.apply(this,arguments);
		this.special_price = json.special_price;
		this.index_special_price_order = json.index_special_price_order;
    },
	 
	 check_special_price_type: function(reward){
		 if(reward.type === 'special_price'){
			 return true;
		 }
		 return false; 
	 },
	 
	 get_special_price: function(){
		return this.special_price;
	 },

	 get_total_with_tax_special_price: function() {
		var rounding = this.pos.currency.rounding;
		var total ;
		
		if(this.get_membership_disc() > 0){
		    total = this.get_total_without_tax() + this.get_total_tax() - this.get_free_products_saleable_price();
		    //total = this.get_total_without_tax() + this.get_total_tax() - (this.get_total_without_tax() * (this.get_membership_disc() /100) - this.get_free_products_saleable_price());
		var ttx = this.get_total_without_tax() + this.get_total_tax();
		        }else{
		            total = this.get_total_without_tax_special_price() + this.get_total_tax_special_price() - this.get_free_products_saleable_price();
		        }
		
		        return Math.round(total);
		
	 },
	 
	 get_total_tax_special_price: function() {
	        var total = 0;
	    	return Math.round(this.orderlines.reduce((function(sum, orderLine) {
	        	total = sum + orderLine.get_tax();
	            return total;
	        }), 0));
	    },
	 
	get_total_without_tax_special_price: function() {
        var total = 0;
        return Math.round(this.orderlines.reduce((function(sum, orderLine) {
            if(!orderLine.product.voucher){
            		total = sum + orderLine.get_price_without_tax();
            }
            return total;
        }), 0));
	    },
	    
	 apply_reward: function(reward){
		 var flag = false;
		 var lines = this.get_orderlines();
		 var index = this.index_special_price_order;
		 var products_to_split = []
		 if(this.check_special_price_type(reward) === true){
			 if (reward.discount_target_type === 'products'){
					for (var i = 0; i < lines.length; i++) {
						var line = lines[i];
						if (this.check_product(line.get_product().id, reward.discount_product_id) == true && !line.is_special_price && this.check_quantity_rule(line, reward)){
							this.set_special_price(line, index);
							flag = true;
							if(this.check_quantity_rule_special_price(line, reward) && line.is_special_price){
								products_to_split.push(line);
							}
						}
					}
					this.split_products(products_to_split);
				 }else if (reward.discount_target_type === 'categories'){
					for (var i = 0; i < lines.length; i++) {
						var line = lines[i];
						if (this.check_category(line.get_product().pos_category_ids, reward.discount_category_ids) == true && !line.is_special_price && this.check_category_quantity_rule(line, reward)){
							this.set_special_price(line, index);
							flag = true;
							if(this.check_quantity_rule_special_price(line, reward) && line.is_special_price){
								products_to_split.push(line);
							}
						}
					}
			     }
		 }
		 if(flag === true){
			 this.special_price = this.special_price + reward.special_price;
			 this.index_special_price_order++;
			 this.trigger('change',this);
		 }else{
			 return _super_posloyalty.prototype.apply_reward.apply(this, arguments)
		 }
	 },
	 
	 check_quantity_rule_special_price: function(line, reward){
		 var rule_reward = this.get_rule_from_reward(reward) || 0;
		 if(rule_reward.qty_rule > 0){
			 if(line.get_quantity() > rule_reward.qty_rule){
				 return true;
			 }
		 }else{
			 if(line.get_quantity() > 1){
				 return true;
			 }
		 }
		 return false;
	 },

	 check_quantity_rule: function(line, reward){
		 var rule_reward = this.get_rule_from_reward(reward) || 0;
		 if(line.get_quantity() >= rule_reward.qty_rule){
			 return true;
		 }
		 return false;
	 },
	 
	 check_category_quantity_rule: function(line, reward){
		 var rule_reward = this.get_rule_from_reward(reward) || 0;
		 if(rule_reward.qty_rule == 0){
			 if(this.get_category_qty(rule_reward.category_ids) >= rule_reward.qty_rule){
				 return true;
			 }
		 }else if(rule_reward.qty_rule > 0){
			 if(this.get_category_qty(rule_reward.category_ids) == rule_reward.qty_rule){
				 return true;
			 }
		 }
		 return false;
	 },
	 
	 get_category_qty: function(category_id){
		 var lines = this.get_orderlines()
		 var line;
		 var total = 0;
		 for(var i=0; i<lines.length; i++){
			 line = lines[i]
			 if(this.check_category(line.get_product().pos_category_ids, category_id)){
				 total = total + line.get_quantity();
			 }
		 }
		 return total
	 },
	 
	 get_rule_from_reward: function(reward){
		 var rule;
		 for (var i = 0; i < this.pos.loyalty.rules.length; i++){
			 rule = this.pos.loyalty.rules[i]
			 if(rule.id == reward.rule_id[0]){
				 return rule
			 }
		 }
		 return null;
	 },
	 
	 set_special_price: function(line, index){
		line.is_special_price = true;
	 	if(!line.index_special_price){
	 		line.index_special_price = index;
	 	}
	 	line.trigger('change',line);
	 },
	 
	 split_products: function(lines){
		 var line;
		 var product;
		 for(var i=0; i < lines.length; i++){
			 line = lines[i];
			 product = this.pos.db.get_product_by_id(line.product.id);
			 this.add_product(product, {
                 quantity: line.get_quantity() - 1,
       		});
			 line.set_quantity(1)
		 }
	 },
	 
	 remove_orderline: function(line){
		 _super_posloyalty.prototype.remove_orderline.apply(this, arguments);
		 this.remove_special_price(line.index_special_price)
	 },
	 
	 remove_special_price: function(index_special_price){
		 var lines = this.get_orderlines();
		 var line;
		 var remove_special_price = false;
		 for(var i=0; i<lines.length; i++){
			 line = lines[i];
			 if(line.index_special_price == index_special_price && line.is_special_price){
				 line.index_special_price = 0;
				 if(this.count_index_special_price(line.index_special_price) == 1 && lines.length > 0){
					 line.is_special_price = false
				 }
				 line.trigger('change',line);
				 remove_special_price = true;
			 }else if(line.is_special_price && this.count_index_special_price(line.index_special_price) == 1){
				 line.index_special_price = 0;
				 line.trigger('change',line);
				 remove_special_price = true
			 }
		 }
		 if(remove_special_price === true){
			 this.special_price = this.special_price - (this.special_price / (this.index_special_price_order - 1));
			 this.index_special_price_order--;
			 remove_special_price = false;
			 this.trigger('change', this)
		 }
		 if(lines.length == 0){
			 this.special_price=0;
			 this.index_special_price_order--;
		 }
	 },
	 
	 count_index_special_price: function(index_special_price){
		 var total = 0
		 var lines = this.get_orderlines();
		 var line;
		 for(var i=0; i<lines.length; i++ ){
			 line = lines[i];
			 if(line.index_special_price == index_special_price && line.is_special_price){
				total = total + 1; 
			 }
		 }
		 return total;
	 },
 });
 
 screens.OrderWidget.include({
	    update_summary: function(){
	        this._super();
	        var order = this.pos.get_order();
	        if (!order.get_orderlines().length) {
	            return;
	        }
	        if(order.get_special_price() > 0){
	        	var special_price  = order ? order.get_special_price() : 0;
	        	this.el.querySelector('.special_price').textContent = this.format_currency(special_price);
	        }
	    },
	});
 
})