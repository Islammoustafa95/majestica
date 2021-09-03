// Copyright (c) 2019, sahil and contributors
// For license information, please see license.txt

/*frappe.provide("majestica.label_print");
majestica.label_print.LabelPrint = Class.extend({
	init: function(args){
		$.extend(this, args);
	},

	item_group: function(){
		var me = this;
		var group = me.frm.doc.item_group;
		if(group){
			frappe.call({
				"method": "majestica.majestica.doctype.label_print.label_print.get_data",
				"args": {"item_group": group},
				"callback": function(r){
					if(r){
						var data = r.message;
						me.frm.clear_table("items");
						for(i=0;i<data.length;i++){
							var child = frappe.model.get_new_doc("Label Item", me.frm.doc, "items");
							$.extend(child, {
								"item_code": data[i].name,
								"price"	: data[i].price
							});

							me.frm.refresh_field("items");
						}
					}
				}
			});
		} else{
			me.frm.clear_table("items");
			me.frm.refresh_field("items");
		}
	}
});
cur_frm.script_manager.make(majestica.label_print.LabelPrint);*/

frappe.ui.form.on("Label Print", {
	add_item: function(frm) {
		console.log(frm);
		if (frm.doc.item !== undefined) {
			frappe.model.get_value(
				"Item",
				frm.doc.item,
				["name", "standard_rate"],
				function(r) {
					if (!r.exc && r) {
						var child = frappe.model.get_new_doc(
							"Label Item",
							me.frm.doc,
							"items"
						);
						$.extend(child, {
							item_code: r.name,
							price: r.standard_rate
						});

						me.frm.refresh_field("items");
					}
				}
			);
		}
	}
});
