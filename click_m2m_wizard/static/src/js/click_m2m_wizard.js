odoo.define('clickm2m.m2m_wizard', function (require) {
 "use strict";


 var core = require('web.core');
 var data = require('web.data');
 var FormView = require('web.FormView');
 var common = require('web.list_common');
 var ListView = require('web.ListView');
 var utils = require('web.utils');
 var Widget = require('web.Widget');
 var Model = require('web.DataModel');
 var QWeb = core.qweb;
 var _t = core._t;
 var relational = require('web.form_relational')

 
relational.FieldMany2ManyTags.include({
	 events: {
		 'click .ui-autocomplete-input': 'click_m2m',
	     
	     'click .o_delete': function(e) {
	            this.remove_id($(e.target).parent().data('id'));
	        },
	     'click .badge': 'open_color_picker',
	     'mousedown .o_colorpicker span': 'update_color',
	     'focusout .o_colorpicker': 'close_color_picker',
	 },
	 click_m2m: function(e){
		 	e.preventDefault();
		 	e.stopPropagation();
	    	console.log("test1",e)
	    	console.log("field", e.delegateTarget.dataset.fieldname)
	    	var self = this
	    	var view =[]
	    	var line_id, model, field , name

	    	if (this !== undefined && this.dataset.parent_view !== undefined ){

	    		line_id = this.dataset.parent_view.datarecord.id
	    		model = this.dataset.parent_view.dataset.model
	    		field = e.delegateTarget.dataset.fieldname
	    		
	    		if (model == "sale.order.line"){
	    			if (field.indexOf("discount") >= 0){
	    				view = "discount.so.wizard";
	    				name = "Discounts" ;
	    			}
	    			

	    		}
	    		if (model == "purchase.order.line"){
	    			if (field.indexOf("tax") >= 0){
	    				view = "tax.po.wizard";
	    				name = "Taxes" ;
	    			}
	    		}
	    		if (model == "account.invoice.line"){
	    			if (field.indexOf("tax") >= 0){
	    				view = "tax.ai.wizard";
	    				name = "Taxes" ;

	    			}
	    			if (field.indexOf("discount") >= 0){
	    				
	    				view = "discount.ai.wizard";
	    				name = "Discounts" ;
    				
	    			}
	    		}
	    		

	    		var view_name = ['discount.ai.wizard' , 'tax.ai.wizard','discount.so.wizard','tax.po.wizard']
		    	var viewm = new openerp.web.Model('ir.ui.view');
				viewm.query(['id','name']).filter([['name', 'in', view_name]]).limit(5).all().then(function(ir_model_datas) {
				    console.log("view :",ir_model_datas)
				    var v_id 
				    console.log("view untuk perbandingan :",view)
				    for (var i in ir_model_datas) {
				    	console.log("view dari get ",ir_model_datas[i].name)
				        if (ir_model_datas[i].name == view){
				        	v_id = ir_model_datas[i].id
				        }
				       
				        
				     }

				    self.do_action({

			                type: 'ir.actions.act_window',
			                res_model: model,
			                name:name,
			                res_id : line_id,
			                views: [[v_id, "form"]],
			                target: 'new',
			              
			                
			               
			            });

			});

	    	}
	         
	        
	    },
	 
 });

});
