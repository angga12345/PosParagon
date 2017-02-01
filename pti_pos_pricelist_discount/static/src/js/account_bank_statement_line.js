odoo.define('pti_pos_pricelist_discount.account_bank_statement_line', function (require) {
 "use strict";
 
 //var parse_value = require('web.web_client');
 //var formats = require('web.formats');
 var models = require('point_of_sale.models');
 var screens = require('point_of_sale.screens');
 var core = require('web.core');
 var QWeb = core.qweb;
 
 //point_of_sale.models
 var _super_paymentline = models.Paymentline;
 models.Paymentline = models.Paymentline.extend({
     initialize: function (attributes, options) {
    	_super_paymentline.prototype.initialize.apply(this,arguments);
 		this.traceno = 0;
 		this.apprcode = 0;
     },
     //set trace no
     set_traceno: function(value){
         this.order.assert_editable();
         this.traceno = value; 
         this.trigger('change',this);
     },
     //set apprcode no
     set_apprcode: function(value){
         this.order.assert_editable();
         this.apprcode = value; 
         this.trigger('change',this);
     },
     //get trace no
     get_traceno: function(){
         return this.traceno;
     },
     //get apprcode no
     get_apprcode: function(){
         return this.apprcode;
     },
     // returns the associated cashregister
     //exports as JSON for server communication
     export_as_JSON: function(){
    	 var json = _super_paymentline.prototype.export_as_JSON.apply(this,arguments);
         json.trace_no = this.get_traceno();
         json.appr_code = this.get_apprcode();
         return json;
     },
     //exports as JSON for receipt printing
     export_for_printing: function(){
    	 var json = _super_paymentline.prototype.export_for_printing.apply(this,arguments);
         json.trace_no = this.get_traceno();
         json.appr_code = this.get_apprcode();
         return json;
     },
 });
 
 
//point_of_sale.screens
 screens.PaymentScreenWidget.include({
	    template:      'PaymentScreenWidget',
	    back_screen:   'product',
	    init: function(parent, options) {
			this._super(parent, options);
			this.trace_mode = "false";
	        this.apprcode_mode = "false";
	        this.pay_mode = "false";
			this.inputtracenobuffer = "";
	        this.inputapprcodebuffer = "";
			this.firstinputtrace = true;
	        this.firstinputapprcode = true;
		},	

		reset_input: function(){
			var line = this.pos.get_order().selected_paymentline;
			this._super();
			this.firstinputapprcode = true;
	        if (line) {
		        if(line.get_traceno()){
		        	this.inputtracenobuffer = line.get_traceno().toString();
		        }else if(line.get_apprcode()){
		        	this.inputapprcodebuffer = line.get_apprcode().toString();
		        }else{
			        this.inputtracenobuffer = ""	
			        this.inputapprcodebuffer = ""	
		        }
	        }else{
		        this.inputtracenobuffer = ""
		        this.inputapprcodebuffer = ""
	        }
		},

		click_paymentmethods: function(id) {
	        var cashregister = null;
	        for ( var i = 0; i < this.pos.cashregisters.length; i++ ) {
	            if ( this.pos.cashregisters[i].journal_id[0] === id ){
	                cashregister = this.pos.cashregisters[i];
	                break;
	            }
	        }
	        if (cashregister.journal.type == 'bank' ){
	        	this.trace_mode = "false";
	        	this.pay_mode = "false";
	        	this.apprcode_mode = "false";
	        }else {
	        	this.trace_mode = "false";
	        	this.pay_mode = "false";
	        	this.apprcode_mode = "false";
	        }
	        this._super(id)
	    },
	    
	    payment_input: function(input) {
	    	this._super(input)
	        var newbuf ;
	        var newbufbatch ;
	        var newbuftrace;
	        var newbufapprcode;
	        
			if(this.trace_mode == "true"){
	    		newbuftrace = this.gui.numpad_input(this.inputtracenobuffer, input, {'firstinputtrace': this.firstinputtrace});
	    		this.firstinputtrace = (newbuftrace.length === 0);
	    		if (newbuftrace !== this.inputtracenobuffer) {
		        	
		            this.inputtracenobuffer = newbuftrace;
		            var order = this.pos.get_order();
		            if (order.selected_paymentline) {
		                var trace = this.inputtracenobuffer;
		
		                if (this.inputtracenobuffer !== "-") {
		                    trace = this.inputtracenobuffer;
		                }
		
		                order.selected_paymentline.set_traceno(trace);
		                this.order_changes();
		                this.render_paymentlines();
		                this.$('.paymentline.selected .edit').text(trace);
		            }
		        }
	    	}else if(this.apprcode_mode == "true"){
	    		newbufapprcode = this.gui.numpad_input(this.inputapprcodebuffer, input, {'firstinputapprcode': this.firstinputapprcode});
	    		this.firstinputapprcode = (newbufapprcode.length === 0);
	    		if (newbufapprcode !== this.inputapprcodebuffer) {
		        	
		            this.inputapprcodebuffer = newbufapprcode;
		            var order = this.pos.get_order();
		            if (order.selected_paymentline) {
		                var apprcode = this.inputapprcodebuffer;
		
		                if (this.inputapprcodebuffer !== "-") {
		                	apprcode = this.inputapprcodebuffer;
		                }
		
		                order.selected_paymentline.set_apprcode(apprcode);
		                this.order_changes();
		                this.render_paymentlines();
		                this.$('.paymentline.selected .edit').text(apprcode);
		            }
		        }
	    	}
	    	else if (this.pay_mode == "true"){
	        	newbuf = this.gui.numpad_input(this.inputbuffer, input, {'firstinput': this.firstinput});
	        	this.firstinput = (newbuf.length === 0);
	        	if (newbuf !== this.inputbuffer) {
		            this.inputbuffer = newbuf;
		            var order = this.pos.get_order();
		            if (order.selected_paymentline ) {
		                var amount = this.inputbuffer;
		
		                if (this.inputbuffer !== "-") {
		                    amount = formats.parse_value(this.inputbuffer, {type: "float"}, 0.0);
		                }
		
		                order.selected_paymentline.set_amount(amount);
		                this.order_changes();
		                this.render_paymentlines();
		                this.$('.paymentline.selected .edit').text(this.format_currency_no_symbol(amount));
		            }
		        }
	        }
	    },
	      
        render_paymentlines: function() {
        	this._super()
        	var self  = this;
            var order = this.pos.get_order();
            if (!order) {
                return;
            }

            var lines = order.get_paymentlines();
            var due   = order.get_due();
            var extradue = 0;
            if (due && lines.length  && due !== order.get_due(lines[lines.length-1])) {
                extradue = due;
            }


            this.$('.paymentlines-container').empty();
            var lines = $(QWeb.render('PaymentScreen-Paymentlines', { 
                widget: this, 
                order: order,
                paymentlines: lines,
                extradue: extradue,
            }));

            lines.on('click','.delete-button',function(){
                self.click_delete_paymentline($(this).data('cid'));
            });
            lines.on('click','td#input_batch',function(){
                if (self.batch_mode == "false"){
                	document.getElementById('input_batch').className = 'col-tendered edit';
                	document.getElementById('input_trace').className = '';
                	document.getElementById('pay').className = '';
                	document.getElementById('input_apprcode').className = '';
                	self.apprcode_mode = "false";
                	self.batch_mode = "true" ;
                	self.trace_mode = "false" ;
                	self.pay_mode = "false" ;
                }
            });
            lines.on('click','td#input_trace',function(){
                if (self.trace_mode == "false"){
                	self.trace_mode = "true" ;
                	self.batch_mode = "false";
                	self.pay_mode = "false" ;
                	self.apprcode_mode = "false";
                	document.getElementById('input_batch').className = '';
                	document.getElementById('pay').className = '';
                	document.getElementById('input_apprcode').className = '';
                	document.getElementById('input_trace').className = 'col-tendered edit';
                }
            });
            lines.on('click','td#input_apprcode',function(){
                if (self.apprcode_mode == "false"){
                	self.apprcode_mode = "true" ;
                	self.batch_mode = "false";
                	self.pay_mode = "false" ;
                	self.trace_mode = "false" ; 
                	document.getElementById('input_apprcode').className = 'col-tendered edit';
                	document.getElementById('input_batch').className = '';
                	document.getElementById('pay').className = '';
                	document.getElementById('input_trace').className = '';
                }
            });
            lines.on('click','td#pay',function(){
                if (self.pay_mode == "false"){
                	self.pay_mode = "true" ;
                	self.batch_mode = "false";
                	self.trace_mode = "false" ;
                	self.apprcode_mode = "false";
                	document.getElementById('input_apprcode').className = '';
                	document.getElementById('input_batch').className = '';
                	document.getElementById('input_trace').className = '';
                	document.getElementById('pay').className = 'col-tendered edit';
                }
            });

            lines.on('click','.paymentline',function(){
                self.click_paymentline($(this).data('cid'));
            });
                
            lines.appendTo(this.$('.paymentlines-container'));
        },
	});
 
});