odoo.define('pti_hide_ba_warning.gui', function (require) {
"use strict";

var gui = require('point_of_sale.gui');
var core = require('web.core');
var Model = require('web.DataModel');

gui.Gui.include({
  _close : function(){
		var self = this
		var current_session = this.pos.pos_session.id
		var posSessionModel = new Model('pos.session');
		posSessionModel.call('confirm_close', [current_session])
		this._super();
	},
  })
});
