frappe.listview_settings['Invoice Consolidation'] = {
	
	onload: function (doclist) {
		// const action = () => {
		// 	const selected_docs = doclist.get_checked_items();
		// 	const docnames = doclist.get_checked_items(true);

		// 	if (selected_docs.length > 0) {
				
        //          console.log(docnames)
		// 		frappe.call({
                   
        //             method: "majestica.doctype.invoice_consolidation.invoice_consolidation.consolidate",
        //             args: {
        //                 "source_names": docnames,
        //             },
        //             callback: function (r) {
        //                 if (!r.exc) {
        //                     frappe.model.sync(r.message);
        //                     cur_frm.dirty();
        //                     cur_frm.refresh();
        //                 }
        //             }
        //         });
		// 	};
		// };

		// doclist.page.add_actions_menu_item(__('Consolidate'), action, false);
	}
};
