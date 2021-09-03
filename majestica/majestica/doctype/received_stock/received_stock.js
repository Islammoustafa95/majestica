// Copyright (c) 2019, sahil and contributors
// For license information, please see license.txt

frappe.provide("majestica.received_stock");
majestica.received_stock.ReceivedStock = Class.extend({
	init: function(args){
		$.extend(this, args);
	},
	get_data: function(){
		var me = this;
		var po = me.frm.doc.po_consolidation;
		var stock = me.frm.doc.stock_arrival;
		if(po && stock){
			frappe.call({
				"method": "majestica.majestica.doctype.received_stock.received_stock.get_data",
				"args": {"po": po, "stock": stock},
				"callback": function(r){
					if(r){
						var data = r.message;
						me.frm.clear_table("received_item");
						for(i=0;i<data.length;i++){
							var child = frappe.model.get_new_doc("Received Item", me.frm.doc, "received_item");
							$.extend(child, {
								"item_code": data[i].item_code,
								"uom": data[i].uom,
								"qty": data[i].qty,
								"total_qty": data[i].total_qty,
								"conversion_factor": data[i].conversion_factor,
								"cbm_info": data[i].cbm_info,
								"received_qty": data[i].received_qty
							});
						}
						me.frm.refresh_field("received_item")
					}
				}
			});
		} else{
			frappe.msgprint("Please select PO Consolidation & Stock Arrival to get the Data.")
		}
	}
});
cur_frm.script_manager.make(majestica.received_stock.ReceivedStock);
