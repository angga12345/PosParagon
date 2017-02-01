odoo.define('pti_pos_sequence_number.gui_extend', function (require) {
 "use strict";
var gui = require('point_of_sale.gui');

gui.Gui.include({
	_close: function(){
		var self = this;
		this._super();
		this.pos.next_order_automatically();
	},
});
})