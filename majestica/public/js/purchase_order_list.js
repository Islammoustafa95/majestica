frappe.listview_settings['Purchase Order'] = {
	add_fields: ["base_grand_total", "company", "currency", "supplier",
		"supplier_name", "per_received", "per_billed", "status"],
	get_indicator: function (doc) {
		if (doc.status === "Closed") {
			return [__("Closed"), "green", "status,=,Closed"];
		} else if (doc.status === "Delivered") {
			return [__("Delivered"), "green", "status,=,Closed"];
		} else if (flt(doc.per_received, 2) < 100 && doc.status !== "Closed") {
			if (flt(doc.per_billed, 2) < 100) {
				return [__("To Receive and Bill"), "orange",
					"per_received,<,100|per_billed,<,100|status,!=,Closed"];
			} else {
				return [__("To Receive"), "orange",
					"per_received,<,100|per_billed,=,100|status,!=,Closed"];
			}
		} else if (flt(doc.per_received, 2) == 100 && flt(doc.per_billed, 2) < 100 && doc.status !== "Closed") {
			return [__("To Bill"), "orange", "per_received,=,100|per_billed,<,100|status,!=,Closed"];
		} else if (flt(doc.per_received, 2) == 100 && flt(doc.per_billed, 2) == 100 && doc.status !== "Closed") {
			return [__("Completed"), "green", "per_received,=,100|per_billed,=,100|status,!=,Closed"];
		}
	},
	onload: function (listview) {
		var method = "erpnext.buying.doctype.purchase_order.purchase_order.close_or_unclose_purchase_orders";

		listview.page.add_menu_item(__("Close"), function () {
			listview.call_for_selected_items(method, { "status": "Closed" });
		});

		listview.page.add_menu_item(__("Re-open"), function () {
			listview.call_for_selected_items(method, { "status": "Submitted" });
		});

		listview.page.add_menu_item(__("Combine PO"), function () {
			var frm = cur_list.get_checked_items()
			if(frm.length > 1){
				var name = []
				for(i=0;i<frm.length;i++){
					name.push(frm[i].name);
				}
				frappe.call({
					"method": "majestica.whitelisted.get_po_items",
					"args": {"data": name},
					"callback": function(r){
						if(r && r.message){
							var data = r.message;
							var po = frappe.model.get_new_doc("PO Consolidation");
							$.extend(po, {
								"title": ("Conbined PO's "+ name.join(" "))
							});
							frappe.model.with_doctype("PO Consolidation", function(){
								for(j=0;j<name.length;j++){
									var child = frappe.model.get_new_doc("Linked PO", po, "linked_po");
									$.extend(child, {
										"purchase_order": frm[j].name,
										"supplier": frm[j].supplier
									});
								}
								for(i=0;i<data.length;i++){
									var item = frappe.model.get_new_doc("Goods Item", po, "items");
									$.extend(item, {
										"item_code": data[i].item_code,
										"qty": data[i].qty
									});
								}
								frappe.set_route("Form", "PO Consolidation", po.name);
							});
						}
					}
				});
			} else{
				frappe.msgprint("Please Select At-least 2 PO for combine.");
			}
		});
	}
};
