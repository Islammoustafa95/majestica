// Copyright (c) 2016, sahil and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer Discount Summary"] = {
	"filters": [
		{
                        "fieldname":"from_date",
                        "label": __("From Date"),
                        "fieldtype": "Date",
                        "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
                        "width": "60px"
                },
		{
                        "fieldname":"to_date",
                        "label": __("To Date"),
                        "fieldtype": "Date",
                        "width": "60px"
                },
	]
}
