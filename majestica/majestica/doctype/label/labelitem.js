frappe.ui.form.on("Label Item", "barcode", function(frm, cdt, cdn) {
	console.log("NNNNNNNN");
    	var d = locals[cdt][cdn];
	// var docs = frappe.model.get_all_docs("Item");
        //frappe.db.get_value("Item", {"item_barecodes": d.barcode}, ['item_name'], function(value) {
          	//d.item_code = value.item_code;
	//console.log("value\n");
	// console.log(docs);
	console.log("---");
        //});
});