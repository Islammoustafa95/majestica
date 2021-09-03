

var Controller = erpnext.accounts.SalesInvoiceController.extend({
	init: function(args){
		$.extend(this, args);
	},
        after_save: function(){
		var me = this;
		var name = me.frm.doc.name;
		frappe.call({
			"method": "majestica.whitelisted.pos",
			"args": {"name": name}
		});
	},
});

cur_frm.script_manager.make(Controller);
