odoo.define('pti_pos_discount_time.loyalty', function (require) {
 "use strict";

	var models = require('point_of_sale.models');
	var DateUtils = require('pti_pos_discount_time.date_utils');
	
	models.load_models([
	    {
	        model: 'loyalty.rule.time',
	        condition: function(self){ return !!self.loyalty; },
	        fields: ['day', 'start_hour', 'end_hour', 'loyalty_rule_id'],
	        domain: function(self){ 
	        	var rule_ids = [];
	        	for(var i=0;i<self.loyalty.rules.length;i++){
	        		rule_ids.push(self.loyalty.rules[i].id)
	        	}
	        	return [['loyalty_rule_id','in', rule_ids]]; 
	        },
	        loaded: function(self,rule_times){
	            self.rule_times = rule_times;
	        },
	    }
	]);

	var _super_posmodel = models.PosModel.prototype;
	 models.PosModel = models.PosModel.extend({
	     initialize: function (session, attributes) {
	         var rule_model = _.find(this.models, function(model){ return model.model === 'loyalty.rule'; });
	         rule_model.fields.push('use_hour_rules');
	         return _super_posmodel.initialize.call(this, session, attributes);
	     },
	 });
	
	var _super_loyalty = models.Order;
	models.Order = models.Order.extend({
		get_available_rewards_automatic: function(){
			var date = new Date();
			var start_date = new Date(this.pos.loyalty.start_date);
			var end_date = new Date(this.pos.loyalty.end_date);

			date.setHours(0, 0, 0, 0);
			start_date.setHours(0, 0, 0, 0);
			end_date.setHours(0, 0, 0, 0);
			if (this.check_date(date, start_date, end_date) === true){
				return _super_loyalty.prototype.get_available_rewards_automatic.apply(this, arguments)
			}
			return false;
		},

		get_rules_active_id: function(){
			var rules = _super_loyalty.prototype.get_rules_active_id.apply(this, arguments);
			for(var i=0;i<rules.length;i++){
				var rule = rules[i];
				if(this.check_rule_time(rule.active_id) === false && rule.use_hour_rules === true){
					rules.splice(0,rules.length)
				}
			}
			return rules;
		 },
		
		check_use_rule_times: function(rule_id){
			var rules = this.pos.loyalty.rules;
			for(var i=0;i<rules.length;i++){
				var rule = rules[i];
				if(rule.use_hour_rules === true && rule.id == rule_id){
					return true;
				}
			}
			return false;
		},
		
		check_rule_time: function(rule_id){
			if(this.check_use_rule_times(rule_id) === true){
				var date = new Date();
				var rule_times = this.pos.rule_times;
				var start_hour, end_hour;
				
				for(var i=0; i<rule_times.length; i++){
					var day = rule_times[i].day;
					start_hour = rule_times[i].start_hour;
					end_hour = rule_times[i].end_hour;
					if (this.check_rule_id(rule_id, rule_times[i].loyalty_rule_id[0]) === true && this.check_day(date, day) === true && 
						this.check_hour(date, start_hour, end_hour) === true){
						return true;
					}
				}
			}
			return false;
		},

		check_rule_id: function(rule_id, rule_time){
			if(rule_id === rule_time){
				return true;
			}
			return false;
		},
		
		check_date: function(date, start_date, end_date){
			if (date >= start_date && date <= end_date){
				return true;
			}
			return false;
		},
		
		check_day: function(date, day){
			var dateUtils = new DateUtils(date.getDay(), date.getHours(), date.getMinutes());
			if(dateUtils.convertDay() === day.toLowerCase()){
				return true;
			}
			return false;
		},
		
		check_hour: function(date, start_hour, end_hour){
			var dateUtils = new DateUtils(date.getDay(), date.getHours(), date.getMinutes());
			var floatHour = dateUtils.convertHourToFloat();
			if (floatHour >= start_hour && floatHour <= end_hour){
				return true;
			}
			return false;
		}
	});

})