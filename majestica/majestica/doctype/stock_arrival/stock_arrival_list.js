frappe.listview_settings['Stock Arrival'] = {
	onload: function(listview){
		listview.page.add_menu_item(__("Combine Arrival"), function () {
			var frm = cur_list.get_checked_items()
			if(frm.length > 1){
				var name = []
				for(i=0;i<frm.length;i++){
					if(frm[i].docstatus == 1){
						name.push(frm[i].name);
					}
				}
				if(name.length > 1){
					frappe.call({
						"method": "majestica.whitelisted.combine_arrial",
						"args": {"name": name},
						"callback": function(r){
							console.log(r);
						}
					});
				} else{
					frappe.msgprint("Please Select only Submitted Doc.");
				}

			} else{
				frappe.msgprint("Please Select at-least 2 Doc to Combine.");
			}
		});	
	}
}
