// Copyright (c) 2018, sahil and contributors
// For license information, please see license.txt


frappe.provide("majestica.stock_arrival");
majestica.stock_arrival.StockArrival = Class.extend({
	init: function(args){
		$.extend(this, args);
	},

	onload: function(frm) {
		cur_frm.add_child('items');
		cur_frm.refresh_fields();
	},

	before_save: function(frm) {
		var idx = 1;
		cur_frm.doc.items.sort(function(a,b){
		  if (a.item_code < b.item_code){ return -1 }
		  else if ( a.item_code > b.item_code){ return 1 }
		  return 1;
		});
		
		cur_frm.doc.items.map(function(item){
		  item.idx = idx++;
		});
	},
	
	search_item: function(frm, cdt, cdn) {
		if (cur_frm.doc.search_item) {
			var frm = this.frm
			var child = locals[cdt][cdn];
			var a = cur_frm.doc.search_item;
			var b = cur_frm.doc.items;
			var c = b.filter(cls => a.includes(cls.barcode));
			if (c.length == 1) {
				var i = cur_frm.doc.items.map(function(e) { return e.barcode; }).indexOf(cur_frm.doc.search_item);
				var j = cur_frm.doc.items[i];
				j.received_qty += 1;
				j.qty = j.received_qty * j.uom_conversion_factor;
				cur_frm.refresh_field('items');
			} else {
				// var d = frappe.model.add_child(cur_frm.doc, "Stock Arrival", "items");
				// d.barcode = frm.doc.search_item;
				var d = frm.add_child("items");
				frappe.model.set_value(d.doctype, d.name, "barcode", a)
				update_item(frm, cdt, cdn, d);
			}			
		}
		reset_search_field();
	},

	barcode: function(args, cdt, cdn){
		var me = this;
		var par = me.frm.doc;
		var child = locals[cdt][cdn];
		if(child.barcode){
			frappe.call({
				"method": "majestica.majestica.doctype.stock_arrival.stock_arrival.get_data",
				"args": {"barcode": child.barcode},
				"callback": function(r){
					if(r){
						var data = r.message[0];
						console.log(data);
						$.extend(child, {
							"item_code": data.name ? data.name : data.parent,
							"uom_conversion_factor": data.uom_conversion_factor
						});
						me.frm.refresh_field("items");
					}
				}
			});
		}
	},

	received_qty: function(agrs, cdt, cdn){
		var me = this;
		var child = locals[cdt][cdn];
		if(child.received_qty){
			var total = 0;
			total = child.received_qty * child.uom_conversion_factor;
			$.extend(child, {
				"qty": total
			});
			me.frm.refresh_field("items");
		}
	},

	before_submit: function(){
		var me = this;
		console.log(me.frm.doc.name);
		frappe.call({
			"method": "majestica.majestica.doctype.stock_arrival.stock_arrival.get_final_data",
			"args": {"name": me.frm.doc.name},
			"callback": function(r){
				if(r){
					console.log(r);
					me.frm.clear_table("arrival_items");
					var data = r.message;
					for(i=0;i<data.length;i++){
						var child = frappe.model.get_new_doc("Final Arrival Items", me.frm.doc, "arrival_items");
						$.extend(child, {
							"item_code": data[i].item_code,
							"qty": data[i].qty
						});
					}
				}
			}
		});
	}

});
cur_frm.script_manager.make(majestica.stock_arrival.StockArrival);

function update_item(frm, cdt, cnd, d) {
	var frm = this.frm;
	frappe.call({
		"method": "majestica.majestica.doctype.stock_arrival.stock_arrival.get_data",
		"args": {"barcode": d.barcode},
		"callback": function(r){
			if(r){
				var data = r.message[0];
				console.log(data);
				var item_code = data.name ? data.name : data.parent;
				var total = d.received_qty * d.uom_conversion_factor;
				// d.received_qty = 1;
				// d.uom_conversion_factor = data.uom_conversion_factor;
				// d.qty = d.received_qty * d.uom_conversion_factor;	
				frappe.model.set_value(d.doctype, d.name, "item_code", item_code);
				frappe.model.set_value(d.doctype, d.name, "received_qty", 1);
				frappe.model.set_value(d.doctype, d.name, "uom_conversion_factor", data.uom_conversion_factor);
				frappe.model.set_value(d.doctype, d.name, "received_qty", 1);
				var total = d.received_qty * d.uom_conversion_factor;
				frappe.model.set_value(d.doctype, d.name, "qty", total);
				console.log(d.total)
			}
			cur_frm.refresh_field('items');
		}
	});
}

function reset_search_field() {
	cur_frm.set_value('search_item', '');
}
