// Copyright (c) 2020, sahil and contributors
// For license information, please see license.txt

frappe.ui.form.on('Invoice Consolidation', {
	refresh: function(frm) {

	},
	before_submit: function(frm) {
		var table = cur_frm.doc.items;
		if (frm.doc.cbm_info > 0){
			return true;
		}
		var cbm_total = 0;
		if(table){
			for(var i=0;i<table.length;i++){
				cbm_total += table[i].cbm_info;
			}
		}
		frappe.model.set_value("Invoice Consolidation", cur_frm.doc.name, "cbm_total", cbm_total);
	}
});
