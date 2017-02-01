odoo.define('pti_pos_sequence_number.pos_models', function (require) {
 "use strict";
 
var models = require('point_of_sale.models');


var _super_posmodel = models.PosModel.prototype;
models.PosModel = models.PosModel.extend({
  next_order_automatically: function(){
  	var unpaid_orders = this.get_order_list()
  	for(var i=0;i<=unpaid_orders.length;i++){
  		var order = unpaid_orders[i]
  		if(order){
  			this.db.remove_unpaid_order(order)
  		}
  	}
  },
});

var _super_order = models.Order.prototype;
models.Order = models.Order.extend({
    initialize: function() {
        _super_order.initialize.apply(this,arguments);
        this.sequence_number = this.pos.config.sequence_number - 1
    },
    init_from_JSON: function(json) {
        _super_order.init_from_JSON.apply(this,arguments);
        this.pos.config.sequence_number = Math.max(this.sequence_number+1,this.pos.config.sequence_number);
    },
});

})