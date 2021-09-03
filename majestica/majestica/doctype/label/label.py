# -*- coding: utf-8 -*-
# Copyright (c) 2019, sahil and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document


from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from frappe.utils import cstr, flt, getdate, new_line_sep, nowdate, add_days
from datetime import date, datetime, timedelta
from frappe.utils.background_jobs import enqueue
import requests
import json

import frappe



class Label(Document):
	def validate(self):
		for i in self.items:
			if not self.purchase_invoice:
				if i.barcode:
					data = get_searchbarcode_rate(i.barcode, self.price_list)
					i.rate = data[0][0]
					i.barcode = i.barcode
					i.item_code = data[0][1]
				elif i.item_code:
					data = get_price(i.item_code, self.price_list)
					i.item_code = i.item_code
					i.price = data



@frappe.whitelist()
def set_barcode_item(barcode):
		parent = frappe.db.sql(""" select parent from `tabItem Barcodes` where barcode=%s""",(barcode), as_dict=True)
		if len(parent) != 0:
			try:
				price_doc  = frappe.get_all("Item Price", filters={"item_code":parent[0]["parent"]}, fields=["*"])[0]
				price = price_doc.price_list_rate
			except:
				price = 0.00

			return {"item_code":parent[0]["parent"],"price":price}
		else:
			frappe.msgprint("Barcode Not Fount","Message")




@frappe.whitelist()
def get_item_code_price(item_code):
	# search barcode no
	# barcode_data = frappe.db.get_value('Item Barcode', {'item_code': item_code}, ['barcode', 'parent as item_code', 'item_price'], as_dict=True)
	data = []
	data = frappe.db.sql(""" select i.item_code , b.item_price , b.barcode from `tabItem` i left join `tabItem Barcode` b
		on i.name = b.parent where i.name = "{}" """.format(item_code), as_list = 1)
	return data;


@frappe.whitelist()
def get_barcode_price(barcode):
	# search barcode no
	# barcode_data = frappe.db.get_value('Item Barcode', {'item_code': item_code}, ['barcode', 'parent as item_code', 'item_price'], as_dict=True)
	data = []
	data = frappe.db.sql(""" select i.item_code , b.item_price , b.barcode from `tabItem` i left join `tabItem Barcode` b
		on i.name = b.parent where b.barcode = "{}"  """.format(barcode),  as_list = 1)
	return data;

@frappe.whitelist()
def get_searchbarcode_rate(barcode, price_list = None):
	b_rate = 0.0
	data = []
	itemcode= frappe.db.get_value('Item Barcodes', 
		{'barcode': barcode,
		},['parent'])
	if itemcode:
		barcode_rate = get_price(itemcode, price_list)
		if barcode_rate:
			data.append([barcode_rate,itemcode])
	return data

# @frappe.whitelist()
# def get_item_code_price_2(barcode, price_list = None):
# 	# search barcode no
# 	# barcode_data = frappe.db.get_value('Item Barcode', {'item_code': item_code}, ['barcode', 'parent as item_code', 'item_price'], as_dict=True)
# 	data = []
# 	b_rate = 0.0
# 	frappe.db.get.value()
# 	data = frappe.db.sql(""" select i.item_code , b.barcode from `tabItem` i left join `tabItem Barcode` b
# 		on i.name = b.parent where b.barcode  = "{}" """.format(barcode), as_list = 1)
# 	if data:
# 		itemcode = data[0][0]
# 		barcode_rate = get_price(itemcode, price_list)
# 		if barcode_rate:
# 			b_rate =  barcode_rate
# 	return 0.0


@frappe.whitelist()
def get_price(item, price_list=None):
	rate = 0
	if item:
		r = frappe.db.sql("select price_list_rate from `tabItem Price` where selling = 1 and %s between valid_from and valid_upto and item_code = %s and price_list = %s limit 1",(datetime.now(), item, price_list))
		if r:
			if r[0][0]:
				rate = r[0][0]
		else:
			r = frappe.db.sql("select price_list_rate from `tabItem Price` where selling = 1 and (valid_from <= %s or valid_upto >= %s) and item_code = %s and price_list = %s limit 1",(datetime.now(), datetime.now(), item, price_list))
			if r:
				if r[0][0]:
					rate = r[0][0]
			else:
				r = frappe.db.sql("select price_list_rate from `tabItem Price` where selling = 1 and valid_from IS NULL and valid_upto IS NULL and item_code = %s and price_list = %s limit 1",(item, price_list))
				if r:
					if r[0][0]:
						rate = r[0][0]
	return rate
