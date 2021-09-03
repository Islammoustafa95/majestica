# -*- coding: utf-8 -*-
# Copyright (c) 2018, sahil and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _, msgprint, throw

class StockArrival(Document):
	pass
	#def validate(self):
	   # for i, item in enumerate(sorted(self._range, key=lambda item: item.item_code), start=1):
		#item.idx = i	


#@frappe.whitelist()
#def get_item_data(box_barcode, carton_barcode):
#	if(box_barcode):
#		return frappe.db.sql(""" select * from `tabItem Barcodes` where box_barcode = %s  """, box_barcode, as_dict=True)
#	if(carton_barcode):
#		return frappe.db.sql(""" select * from `tabItem Barcodes` where carton_barcode = %s  """, carton_barcode, as_dict=True)


@frappe.whitelist()
def get_data(barcode):
	if(barcode):
		data = []
		try:
			data = frappe.db.sql("""select i.name, ib.parent, ib.uom_conversion_factor 
					from `tabItem` i inner join `tabItem Barcodes` ib on ib.parent = i.name
					where ib.barcode = %s  """,(barcode), as_dict=True)

			if(data):
				return data
			else:
				data = frappe.db.sql("""select i.name, ib.parent, ib.uom_conversion_factor
						from `tabItem` i inner join `tabItem Barcodes` ib on i.name = ib.parent
						where i.barcode = %s """,(barcode), as_dict=True)
				return data

		except Exception as e:
			frappe.msgprint(_("Please take a screen-shoot and send to your System Admin. Error: {0}").format(e))


@frappe.whitelist()
def get_final_data(name):
	if(name):
		data = frappe.db.sql("""select item_code, sum(qty) as qty  from `tabArrival Items` where parent = %s group by `item_code` """,(name), as_dict=True)

		return data
