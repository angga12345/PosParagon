odoo.define('pti_pos_discount_time.date_utils', function (require) {
 "use strict";
 
 	function DateUtils(day, hour, minute){
		this.hour = hour;
		this.minute = minute;
		this.day = day;
 	}

	DateUtils.prototype.convertHourToFloat = function(){
		var floatValue = this.hour + (this.minute / 60);
		return floatValue;
	}

	DateUtils.prototype.convertDay = function(){
		switch(this.day){
			case 1:
				return "monday";
			case 2:
				return "tuesday";
			case 3:
				return "wednesday";
			case 4:
				return "thursday";
			case 5:
				return "friday";
			case 6:
				return "saturday";
			case 7:
				return "sunday";
			default:
				return "";
		}
	}
	return DateUtils;
});