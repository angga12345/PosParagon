odoo.define('pti_pos_special_product_discount.pos_config', function (require) {
 "use strict";

 var models = require('point_of_sale.models');
 
 var _super_posmodel = models.PosModel.prototype;
 models.PosModel = models.PosModel.extend({
	 initialize: function (session, attributes) {
         var loyalty_reward_model = _.find(this.models, function(model){ return model.model === 'loyalty.reward'; });
         loyalty_reward_model.fields.push('discount_text');
         return _super_posmodel.initialize.call(this, session, attributes);
     },
 });
 
 var _super_posorderline = models.Orderline;
 models.Orderline = models.Orderline.extend({
	 	get_price_line_tot_askoko: function(){
	        var rounding = this.pos.currency.rounding;
	        return this.get_unit_price_taxed() * this.get_quantity();
	    },
	    get_price_with_tax_askoko: function(){
	        return this.get_all_prices_askoko().priceWithTax;
	    },
	    get_all_prices_askoko: function(){
	    	var price_unit ;

	    	        price_unit = this.get_unit_price() ;
	    	        var taxtotal = 0;
	    	        var product =  this.get_product();
	    	        var taxes_ids = product.taxes_id;
	    	        var taxes =  this.pos.taxes;
	    	        var taxdetail = {};
	    	        var product_taxes = [];

	    	        _(taxes_ids).each(function(el){
	    	            product_taxes.push(_.detect(taxes, function(t){
	    	                return t.id === el;
	    	            }));
	    	        });

	    	        var all_taxes = this.compute_all(product_taxes, price_unit, this.get_quantity(), this.pos.currency.rounding);
	    	        _(all_taxes.taxes).each(function(tax) {
	    	            
	    	            taxtotal += tax.amount;
	    	            
	    	            taxdetail[tax.id] = tax.amount;
	    	        });

	    	        return {
	    	            "priceWithTax": all_taxes.total_included,
	    	            "priceWithoutTax": all_taxes.total_excluded,
	    	            "tax": taxtotal,
	    	            "taxDetails": taxdetail,
	    	        };
	    },
 });
 
 
 var _super_posloyalty = models.Order;
 models.Order = models.Order.extend({
	 initialize: function(attr,options) {
		 _super_posloyalty.prototype.initialize.apply(this,arguments);
		 this.reward= null;
	 },
	 export_as_JSON: function(){
		var json = _super_posloyalty.prototype.export_as_JSON.apply(this,arguments);
		json.reward = this.reward;
		return json;
    },
    init_from_JSON: function(json){
    	_super_posloyalty.prototype.init_from_JSON.apply(this,arguments);
		this.reward = json.reward
    },
	
	export_for_printing: function(){
		var receipt = _super_posloyalty.prototype.export_for_printing.apply(this, arguments);
		receipt['receipt_show_discount'] = this.get_discount_text(this.pos.config.show_discount);
		receipt['custom_discount_text'] = this.custom_get_discount_text();
		receipt['term_condition_text'] = this.get_term_condition_text();
		receipt['display_term'] = this.get_display_term();
		return receipt;    
	},
//put variables inside javscript strings
	parse: function(str) {
		var args = [].slice.call(arguments, 1),
			i = 0;
			
			return str.replace(/%s/g, function() {
			return args[i++];
		});
	},

//discount text custom
    custom_get_discount_text: function(){
    	if(this.pos.get_order().pos.config.loyalty_id != false){
	    	var rewards = this.get_available_rewards_automatic();
	    	if(rewards.length > 1){
	    		return rewards[0].discount_text;
	    	}
	    	return "";
    	}
    	return "";
    },

    get_grand_total_askoko : function(){
    	return this.get_total_askoko();
    },
 
     get_total_askoko: function() {
     	var rounding = this.pos.currency.rounding;
        var total ;
         
        total = this.get_total_with_tax_askoko();
         
        return Math.round(total);
     },
 
     get_total_with_tax_askoko: function() {
        var total = 0;
        return Math.round(this.orderlines.reduce((function(sum, orderLine) {
            if(!orderLine.product.voucher){
                total = sum + orderLine.get_price_with_tax_askoko();
            }
            return total;
        }), 0));
     },
     
	 //get_discount_text: function(show_discount){
     get_discount_text: function(show_discount){
		if(show_discount == true){
			return true;
		}
		return false;
	 },
	 
	 get_term_condition_text: function(){
		 if(this.pos.loyalty){
			 return this.pos.loyalty.term_condition_text;
		 }
		 return "";
	 },
	 
	 get_display_term: function(){
		 if(this.reward){
			 return this.reward.display_term;
		 }
		 return false
	 },
});
}) 