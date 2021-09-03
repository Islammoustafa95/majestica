// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings['Cap Stock Arrival'] = {
	onload: function (doclist) {
		const action = () => {
			const selected_docs = doclist.get_checked_items();
			const docnames = doclist.get_checked_items(true);

			if (selected_docs.length > 0) {
				
                 console.log(docnames)
				frappe.call({
                   
                    method: "majestica.majestica.doctype.invoice_consolidation.invoice_consolidation.consolidate",
                    args: {
                        "source_names": docnames,
                        "doctype": "Cap Stock Arrival",
                    },
                    callback: function (r) {
                       
							console.log(r.message)
							frappe.set_route('Report','Invoice Consolidation' ,'Invoice Consolidation', {ID: r.message.name});
						
                    }
                });
			};
		};

		doclist.page.add_actions_menu_item(__('Consolidate'), action, false);
	}
};
