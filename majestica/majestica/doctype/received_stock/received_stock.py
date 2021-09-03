# -*- coding: utf-8 -*-
# Copyright (c) 2019, sahil and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _, throw, msgprint

class ReceivedStock(Document):
	pass

@frappe.whitelist()
def get_data(po, stock):
	if(po and stock):
		po_data = frappe.db.sql("""select item_code, qty, uom, conversion_factor, total_qty, cbm_info from `tabGoods Item` where parent = %s """, po, as_dict=True)
		stock_data = frappe.db.sql("""select item_code, qty from `tabFinal Arrival Items` where parent = %s """, stock, as_dict=True)
		frappe.msgprint(_("{0}").format(stock_data))
		item_data = []
		if(po_data and stock_data):
			for p in po_data:
				for s in stock_data:
					if(p.item_code == s.item_code):
						p.update({"received_qty": s.qty})
					#else:
					#	p.update({"received_qty": 0.0})

				item_data.append(p)
			return item_data
		else:
			frappe.throw(_("Items Data not found either in {0} or in {1}. Please Check PO Consolidation and Stock Arrival before Compare.").format(po, stock))
