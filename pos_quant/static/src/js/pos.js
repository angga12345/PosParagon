odoo.define('pos_quant.PosModel', function(require){
"use strict";

    var models = require('point_of_sale.models');
    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            this.quant = null;
            return _super_posmodel.initialize.call(this, session, attributes);
        },
    });

    models.load_models([{
        model: 'stock.quant',
        fields: ['qty','product_id'],
        domain: function(self){ return [['location_id', '=', self.shop.id]]; },
        loaded: function(self, quants){
        	for (var obj in quants){
        		var quant = quants[obj];
        		if (quant.product_id && quant.product_id[0]){
            		self.db.product_by_id[quant.product_id[0]].qty_available = quant.qty;	
        		}
        	}
        },
    },],{'after': 'product.product'});
})
