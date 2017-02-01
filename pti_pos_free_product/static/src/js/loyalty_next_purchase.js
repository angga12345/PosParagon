odoo.define('pti_pos_free_product.loyalty_next_purchase', function (require) {
 "use strict";
 
var models = require('point_of_sale.models');
var _super_posloyalty = models.Order;
var _super_posmodel = models.PosModel.prototype;

models.PosModel = models.PosModel.extend({
    initialize: function (session, attributes) {
        var partner_model = _.find(this.models, function(model){ return model.model === 'loyalty.reward'; });
        partner_model.fields.push('discount_desc');
        return _super_posmodel.initialize.call(this, session, attributes);
    },
});
models.Order = models.Order.extend({
    remove_orderline: function( line ){
        this.discount_desc='';
    	_super_posloyalty.prototype.remove_orderline.apply(this, arguments);
    },
	apply_reward: function(reward){
		var flag = false;
		if (reward.type === 'next_purchase'){
			flag = true;
			this.discount_desc = reward.discount_desc;
		 }
		else{
			return _super_posloyalty.prototype.apply_reward.apply(this, arguments)
		}
    },
    initialize: function(attr,options) {
		_super_posloyalty.prototype.initialize.apply(this,arguments);
		this.discount_desc = '';
	},
	export_as_JSON: function(){
		var json = _super_posloyalty.prototype.export_as_JSON.apply(this,arguments);
		json.discount_desc = this.discount_desc;
		return json;
    },
    init_from_JSON: function(json){
		_super_posloyalty.prototype.init_from_JSON.apply(this,arguments);
		this.discount_desc = json.discount_desc;
    },
});

})