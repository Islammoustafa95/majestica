// Copyright (c) 2018, sahil and contributors
// For license information, please see license.txt



frappe.provide("majestica.pos_closing_voucher");
majestica.pos_closing_voucher.POSClosingVoucher = Class.extend({
	init: function(args){
		$.extend(this, args);
	},
	
	onload: function(frm) {
		if (cur_frm.doc.__islocal) {
			var pos_no = frappe.datetime.now_date() + "-" + frappe.session.user;
			cur_frm.set_value('pos_no', pos_no);
		}
	},

	refresh: function(frm) {
		var frm = this.frm;
		cur_frm.set_value('pos_user', frappe.session.user)
		cur_frm.set_value('user_name', frappe.session.user_fullname)
		if (frm.doc.__islocal && !frm.doc.opening_balance_details && !frm.doc.closing_balance_details) {
			frm.add_child('opening_balance_details').notes = '100';
			frm.add_child('opening_balance_details').notes = '50';
			frm.add_child('opening_balance_details').notes = '20';
			frm.add_child('opening_balance_details').notes = '10';
			frm.add_child('opening_balance_details').notes = '5';
			frm.add_child('opening_balance_details').notes = '1';
			frm.add_child('opening_balance_details').notes = '0.5';
			frm.add_child('opening_balance_details').notes = '0.2';
			frm.add_child('opening_balance_details').notes = '0.1';
			frm.add_child('opening_balance_details').notes = '0.05';
			frm.add_child('opening_balance_details').notes = '0.01';
			frm.add_child('closing_balance_details').cl_notes = '100';
			frm.add_child('closing_balance_details').cl_notes = '50';
			frm.add_child('closing_balance_details').cl_notes = '20';
			frm.add_child('closing_balance_details').cl_notes = '10';
			frm.add_child('closing_balance_details').cl_notes = '5';
			frm.add_child('closing_balance_details').cl_notes = '1';
			frm.add_child('closing_balance_details').cl_notes = '0.5';
			frm.add_child('closing_balance_details').cl_notes = '0.2';
			frm.add_child('closing_balance_details').cl_notes = '0.1';
			frm.add_child('closing_balance_details').cl_notes = '0.05';
			frm.add_child('closing_balance_details').cl_notes = '0.01';
			frm.refresh_field('closing_balance_details');
			frm.refresh_field('opening_balance_details');
		}
	},

	notes: function(frm, cdt, cdn) {
		calculate_total(frm, cdt, cdn);
	},

	notes_number: function(frm, cdt, cdn) {
		calculate_total(frm, cdt, cdn);
	},

	notes_total: function(frm, cdt, cdn) {
		let d = locals[cdt][cdn];
  		frappe.model.set_value(d.doctype, d.name, "notes_total", d.notes * d.notes_number);
		let total = 0;
		cur_frm.doc.opening_balance_details.forEach(function(d){total += d.notes * d.notes_number});
		cur_frm.set_value('opening_balance', flt(total));
	},

	cl_notes: function(frm, cdt, cdn) {
		calculate_total2(frm, cdt, cdn);
	},

	cl_notes_number: function(frm, cdt, cdn) {
		calculate_total2(frm, cdt, cdn);
	},

	cl_notes_total: function(frm, cdt, cdn) {
		let d = locals[cdt][cdn];
  		frappe.model.set_value(d.doctype, d.name, "cl_notes_total", d.cl_notes * d.cl_notes_number);
		let closing_total = 0;
		cur_frm.doc.closing_balance_details.forEach(function(d){closing_total += d.cl_notes * d.cl_notes_number});
		cur_frm.set_value('closing_amount', flt(closing_total));
	},
	
	get_data: function(){
		var frm = this.frm;
		var user = frm.doc.pos_user || "";
		var start = frm.doc.period_start_date || "";
		var end = frm.doc.period_end_date || "";
		if((user == "") || (start == "") || (end == "")){
			frappe.msgprint(__("Please Select the POS User, Period Start Date & Period End Date!"));
			return false;
		} else{
			frappe.call({
				"method": "majestica.majestica.doctype.pos_closing_voucher.pos_closing_voucher.get_invoices",
				"args": {"user": user, "start": start, "end": end },
				"callback": function(r){
					if(r){
						
						frm.clear_table("pos_invoice_item");
						frm.clear_table("pos_mode_of_payment");
						var parent = frm.doc;
						var data = r.message[0];
						var pos_data = r.message[1];
						for(var i=0;i<data.length;i++){
							var child = frappe.model.get_new_doc("POS Invoice Item", frm.doc, "pos_invoice_item");
							$.extend(child, {
								"invoice_name": data[i].name,
								"quantity_of_items": data[i].qty,
								"grand_total": data[i].grand_total
							});
						}

						for(var j=0;j<pos_data.length;j++){
							var pos_child = frappe.model.get_new_doc("POS Mode Of Payment", frm.doc, "pos_mode_of_payment");
							$.extend(pos_child, {
								"mode_of_payment": pos_data[j].name,
								"collected_amount": pos_data[j].amount
							});
						}
					}
				frm.refresh_field("pos_invoice_item");
				frm.refresh_field("pos_mode_of_payment");
				//frm.save();
				}
			});
		}
	},
/*
	before_save: function(){
		var frm = this.frm;
		var payment = frm.doc.pos_mode_of_payment;
		var invoices = frm.doc.pos_invoice_item;
		frm.doc.payment_method_total = 0.0;
		frm.doc.invoices_total = 0.0;
		if(payment){
			var pm_total = 0.0
			for(i=0; i<payment.length;i++){
				pm_total += payment[i].collected_amount;
			}
			frappe.model.set_value(frm.doc.doctype, frm.doc.name, "payment_method_total", pm_total);
		}

		if(invoices){
			var si_total = 0.0
			for(j=0; j<invoices.length;j++){
				si_total += invoices[j].grand_total;	
			}
			frappe.model.set_value(frm.doc.doctype, frm.doc.name, "invoices_total", si_total);
		}
	}
*/
})
cur_frm.script_manager.make(majestica.pos_closing_voucher.POSClosingVoucher);

var calculate_total = function(frm, cdt, cdn) {
	let d = locals[cdt][cdn];
	if (d.notes && d.notes_number) {
		frappe.model.set_value(cdt, cdn, "notes_total", flt(d.notes * d.notes_number));
	} else {
		frappe.model.set_value(cdt, cdn, "notes_total", "");
	}
}

var calculate_total2 = function(frm, cdt, cdn) {
	let d = locals[cdt][cdn];
	if (d.cl_notes && d.cl_notes_number) {
		frappe.model.set_value(cdt, cdn, "cl_notes_total", flt(d.cl_notes * d.cl_notes_number));
	} else {
		frappe.model.set_value(cdt, cdn, "cl_notes_total", "");
	}
}
