// Copyright (c) 2019, sahil and contributors
// For license information, please see license.txt

frappe.ui.form.on("Label", {
	onload_post_render: function(frm){
			frm.add_fetch("item_code","standard_rate","price");	
	},
	item_group: function(frm) {
		if(frm.doc.item_group !== undefined){
			frm.set_query("item", function() {
				return {
					filters: {
						"item_group": frm.doc.item_group
					}
				};
			});
		}	
	}
});

frappe.ui.form.on("Label", {
	add_item: function(frm) {
		if (frm.doc.item !== undefined) {
			frappe.model.get_value("Item", frm.doc.item, ["name", "standard_rate"],	function(r) {
					if (!r.exc && r) {
						var child = frappe.model.get_new_doc("Label Item", frm.doc, "items");
						$.extend(child, {
							item_code: r.name,
							price: r.standard_rate
						});
						frappe.model.set_value(frm.doctype, frm.doc.name, "item", undefined);
						frm.refresh_field("items");
					}
				}
			);
		}
	}
});