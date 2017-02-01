odoo.define('pos_product_available.PosModel', function(require){
"use strict";


    var models = require('point_of_sale.models');
    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var partner_model = _.find(this.models, function(model){ return model.model === 'product.product'; });
            partner_model.fields.push('qty_available');
//            this.quant = null;
            console.log('What is this ? : ', partner_model);
            return _super_posmodel.initialize.call(this, session, attributes);
        },
    });

    var PosModelSuper = models.PosModel;

//    models.load_models([{
//        model: 'stock.quant',
//        fields: ['qty',
//                 'product_id'],
//        domain: function(self){ return [['location_id', '=', self.shop.id]]; },
//        loaded: function(self, quants){
//        	console.log('Cek Quant : ', quants);
//        	for (var obj in quants){
//        		var quant = quants[obj];
//        		if (quant.product_id && quant.product_id[0]){
//            		self.db.product_by_id[quant.product_id[0]].qty_available = quant.qty;	
//        		}
//        	}
//        	console.log('Cek Self : ', self);
//        },
//    },],{'after': 'product.product'});

    models.PosModel = models.PosModel.extend({
        refresh_qty_available:function(product){
            var $elem = $("[data-product-id='"+product.id+"'] .qty-tag");
            $elem.html(product.qty_available);
            if (product.qty_available <= 0 && !$elem.hasClass('not-available')){
                $elem.addClass('not-available');
            }
        },
        push_order: function(order){
            var self = this;
            var pushed = PosModelSuper.prototype.push_order.call(this, order);
            if (order){
                order.orderlines.each(function(line){
                    var product = line.get_product();
                    product.qty_available -= line.get_quantity();
                    self.refresh_qty_available(product);
                });
            }
            return pushed;
        },
        push_and_invoice_order: function(order){
            var self = this;
            var invoiced = PosModelSuper.prototype.push_and_invoice_order.call(this, order);

            if (order && order.get_client()){
                if (order.orderlines){
                    order.orderlines.each(function(line){
                        var product = line.get_product();
                        product.qty_available -= line.get_quantity();
                        self.refresh_qty_available(product);
                    });
                } else if (order.orderlines){
                    order.orderlines.each(function(line){
                        var product = line.get_product();
                        product.qty_available -= line.get_quantity();
                        self.refresh_qty_available(product);
                    });
                }
            }

            return invoiced;
        },
    })
})
