// Copyright (c) 2018, sahil and contributors
// For license information, please see license.txt

frappe.ui.form.on('PO Consolidation', {
	before_submit: function(frm) {
		var table = cur_frm.doc.items;
		var cbm_total = 0;
		if(table){
			for(i=0;i<table.length;i++){
				cbm_total += table[i].cbm_info;
			}
		}
		frappe.model.set_value("PO Consolidation", cur_frm.doc.name, "cbm_total", cbm_total);
	}
});
