odoo.define('pti_pos_voucher.voucher', function (require) {
 "use strict";
var screens = require('point_of_sale.screens');
var gui = require('point_of_sale.gui');
var core = require('web.core');
var Model = require('web.DataModel');
var QWeb = core.qweb;
var _t = core._t;

screens.ProductListWidget.include({
    renderElement: function() {
        var el_str  = QWeb.render(this.template, {widget: this});
        var el_node = document.createElement('div');
            el_node.innerHTML = el_str;
            el_node = el_node.childNodes[1];

        if(this.el && this.el.parentNode){
            this.el.parentNode.replaceChild(el_node,this.el);
        }
        this.el = el_node;

        var list_container = el_node.querySelector('.product-list');
        for(var i = 0, len = this.product_list.length; i < len; i++){
        	if(this.product_list[i] != undefined){
                var product_node = this.render_product(this.product_list[i]);
                product_node.addEventListener('click',this.click_product_handler);
                list_container.appendChild(product_node);
            }
        }
    },

 });




screens.PaymentScreenWidget.include({
  
  validate_order: function(force_validation) {
        var self = this;
        var order = this.pos.get_order();

        // FIXME: this check is there because the backend is unable to
        // process empty orders. This is not the right place to fix it.
        if (order.get_orderlines().length === 0) {
            this.gui.show_popup('error',{
                'title': _t('Empty Order'),
                'body':  _t('There must be at least one product in your order before it can be validated'),
            });
            return;
        }

        // get rid of payment lines with an amount of 0, because
        // since accounting v9 we cannot have bank statement lines
        // with an amount of 0
        order.clean_empty_paymentlines();

        var plines = order.get_paymentlines();
        for (var i = 0; i < plines.length; i++) {
            if (plines[i].get_type() === 'bank' && plines[i].get_amount() < 0) {
                this.pos_widget.screen_selector.show_popup('error',{
                    'message': _t('Negative Bank Payment'),
                    'comment': _t('You cannot have a negative amount in a Bank payment. Use a cash payment method to return money to the customer.'),
                });
                return;
            }
        }

        if (!order.is_paid() || this.invoicing) {
            return;
        }

        // The exact amount must be paid if there is no cash payment method defined.
        if (Math.abs(order.get_total_with_tax() - order.get_total_paid()) > 0.00001) {
            var cash = false;
            for (var i = 0; i < this.pos.cashregisters.length; i++) {
                cash = cash || (this.pos.cashregisters[i].journal.type === 'cash');
            }
            if (!cash) {
                this.gui.show_popup('error',{
                    title: _t('Cannot return change without a cash payment method'),
                    body:  _t('There is no cash payment method available in this point of sale to handle the change.\n\n Please pay the exact amount or add a cash payment method in the point of sale configuration'),
                });
                return;
            }
        }

        // if the change is too large, it's probably an input error, make the user confirm.
        if (!force_validation && (order.get_total_with_tax() * 1000 < order.get_total_paid())) {
            this.gui.show_popup('confirm',{
                title: _t('Please Confirm Large Amount'),
                body:  _t('Are you sure that the customer wants to  pay') + 
                       ' ' + 
                       this.format_currency(order.get_total_paid()) +
                       ' ' +
                       _t('for an order of') +
                       ' ' +
                       this.format_currency(order.get_total_with_tax()) +
                       ' ' +
                       _t('? Clicking "Confirm" will validate the payment.'),
                confirm: function() {
                    self.validate_order('confirm');
                },
            });
            return;
        }

        if (order.is_paid_with_cash() && this.pos.config.iface_cashdrawer) { 

                this.pos.proxy.open_cashbox();
        }

        if (order.is_to_invoice()) {
            var invoiced = this.pos.push_and_invoice_order(order);
            this.invoicing = true;

            invoiced.fail(function(error){
                self.invoicing = false;
                if (error.message === 'Missing Customer') {
                    self.gui.show_popup('confirm',{
                        'title': _t('Please select the Customer'),
                        'body': _t('You need to select the customer before you can invoice an order.'),
                        confirm: function(){
                            self.gui.show_screen('clientlist');
                        },
                    });
                } else if (error.code < 0) {        // XmlHttpRequest Errors
                    self.gui.show_popup('error',{
                        'title': _t('The order could not be sent'),
                        'body': _t('Check your internet connection and try again.'),
                    });
                } else if (error.code === 200) {    // OpenERP Server Errors
                    self.gui.show_popup('error-traceback',{
                        'title': error.data.message || _t("Server Error"),
                        'body': error.data.debug || _t('The server encountered an error while receiving your order.'),
                    });
                } else {                            // ???
                    self.gui.show_popup('error',{
                        'title': _t("Unknown Error"),
                        'body':  _t("The order could not be sent to the server due to an unknown error"),
                    });
                }
            });

            invoiced.done(function(){
                self.invoicing = false;
                order.finalize();
            });
        } else {
            
//            var allproducts = this.pos.db.product_by_id;
//            
//            for(var i= 0; i<order.orderlines.models.length;i++){
//                
//                if (order.orderlines.models[i].product.list_price < 0 && order.orderlines.models[i].product.voucher){
//                    
//                    var prodTemplateModel = new Model('product.product');
//	                prodTemplateModel.call('deactive_voucher', [order.orderlines.models[i].product.id]
//	                          ).then(function (result) {
//	                
//	                });
//                    delete this.pos.db.product_by_id[order.orderlines.models[i].product.id]
//                }
//
//            }
            
            this.pos.push_order(order);
            this.gui.show_screen('receipt');
        }
    },
    
     });

});



