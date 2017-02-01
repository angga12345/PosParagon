odoo.define('view_dashboard.displayperpage', function (require) {
 "use strict";   

var core = require('web.core');
var data = require('web.data');
var Model = require('web.DataModel');
var Dialog = require('web.Dialog');
var form_common = require('web.form_common');
var Pager = require('web.Pager');
var pyeval = require('web.pyeval');
var session = require('web.session');
var utils = require('web.utils');
var View = require('web.View');

var KanbanColumn = require('web_kanban.Column');
var quick_create = require('web_kanban.quick_create');
var KanbanRecord = require('web_kanban.Record');
var kanban_widgets = require('web_kanban.widgets');

var QWeb = core.qweb;
var _lt = core._lt;
var _t = core._t;
var ColumnQuickCreate = quick_create.ColumnQuickCreate;
var fields_registry = kanban_widgets.registry;
console.log("INI Masuk kanban inherit",fields_registry);

var kanbanview = require('web_kanban.KanbanView');
console.log("INI KANBAN TERLOAD :",kanbanview);
var kanbaninherit = kanbanview.include({
    init: function (parent, dataset, view_id, options) {
        this._super(parent, dataset, view_id, options);
        _.defaults(this.options, {
            "quick_creatable": true,
            "creatable": true,
            "create_text": undefined,
            "read_only_mode": false,
            "confirm_on_delete": true,
        });

        // qweb setup
        this.qweb = new QWeb2.Engine();
        this.qweb.debug = session.debug;
        this.qweb.default_dict = _.clone(QWeb.default_dict);

        this.model = this.dataset.model;
        this.limit = options.limit || 10;
        console.log("INI KANBAN TERLOAD limit :",this.limit);
        this.grouped = undefined;
        this.group_by_field = undefined;
        this.default_group_by = undefined;
        this.grouped_by_m2o = undefined;
        this.relation = undefined;
        this.is_empty = undefined;
        this.many2manys = [];
        this.m2m_context = {};
        this.widgets = [];
        this.data = undefined;
        this.model = dataset.model;
        this.quick_creatable = options.quick_creatable;
        this.no_content_msg = options.action && (options.action.get_empty_list_help || options.action.help);
        this.search_orderer = new utils.DropMisordered();
    },

 })

});
