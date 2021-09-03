frappe.listview_settings['Voucher'] = {
	colwidths: {"subject": 6},
	onload: function(listview) {
		// frappe.route_options = {
		// 	"status": "Open"
		// };

		// var method = "erpnext.support.doctype.issue.issue.set_multiple_status";

        listview.page.add_menu_item(__("Bulk Generate"), function() {
            frappe.prompt([
                {'fieldname': 'amount', 'fieldtype': 'Currency', 'label': 'Voucher Amount', 'reqd': 1},
                {'fieldname': 'total', 'fieldtype': 'Int', 'label': 'Total Voucher', 'reqd': 1}  
            ],
            function(values){
                console.log(values['amount']);
                frappe.call({
                    "method": "majestica.majestica.doctype.voucher.voucher.bulk_voucher_generate",
                    "args": {
                        "amount": values['amount'],
                        "total": values['total']
                    },
                    "callback": function(r){
                        console.log(r.message);
                        cur_list.refresh();
                    }
                })
            },
            'Bulk Voucher Generate',
            'Generate'
            )          
		});
	}
}
