# -*- coding: utf-8 -*-
# Copyright (c) 2018, sahil and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from itertools import groupby
from frappe import _, msgprint

class POSClosingVoucher(Document):
	def validate(self):
		self.calculate_total()

	def calculate_total(self):
		self.payment_method_total = 0.0
		self.invoices_total = 0.0
		invoice_items = self.pos_invoice_item
		pos_items = self.pos_mode_of_payment

		if(pos_items):
			for i in pos_items:
				self.payment_method_total += float(i.get("collected_amount"))

		if(invoice_items):
			for j in invoice_items:
				self.invoices_total += float(j.get("grand_total"))

		#self.closing_amount = self.invoices_total + self.opening_balance


@frappe.whitelist()
def get_invoices(user, start, end):
	print(user, start, end)

	data = frappe.db.sql(""" select name, grand_total from `tabSales Invoice` where docstatus != 2 and is_pos = 1 and owner = %s and posting_date between %s and %s""",(user, start, end),as_dict=True)
	payment_data = []
	invoice_data = []
	if(data):
		for d in range(0, len(data)):
			item_qty = frappe.db.sql("""select count(qty) as total_qty from `tabSales Invoice Item` where parent = %s """,data[d]['name'], as_dict=True)
			if(item_qty):
				data[d].update({"qty": item_qty[0]['total_qty']})
	
			pos = (frappe.db.sql("""select sip.mode_of_payment, (sip.amount-si.change_amount) as amount
				 from `tabSales Invoice` si inner join `tabSales Invoice Payment` sip on si.name = sip.parent  where sip.parent = %s """,(data[d]['name']), as_dict=True))
			if(pos):
				payment_data.append(pos)

	for p in payment_data:
		invoice_data.append(p[0])
	final_pos_data = []
	if(invoice_data):
		for k,v in groupby(sorted(invoice_data, key= lambda x: x["mode_of_payment"]), lambda x: x["mode_of_payment"]):
			final_pos_data.append({"name": k, "amount": str(sum(float(j["amount"]) for j in list(v)))})
	
	return data, final_pos_data
