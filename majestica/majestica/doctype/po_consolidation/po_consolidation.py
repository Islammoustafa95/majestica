# -*- coding: utf-8 -*-
# Copyright (c) 2018, sahil and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, _

class POConsolidation(Document):

	def validate(self):
		self.update_values()

	def  update_values(self):
		value = []
		for po in self.linked_po:
			for item in self.items:
				data = frappe.db.sql("""select item_code, conversion_factor, uom from `tabPurchase Order Item` where item_code = %s and parent = %s """, (item.get('item_code'), po.get('purchase_order')), as_dict=True)
				if(data):
					value.append(data[0])
					
		for i in self.items:
			for v in value:
				if(i.get("item_code") == v.item_code):
					cbm = []
					try:
						cbm = frappe.db.get_values("Item", filters={"item_code":v.item_code}, fieldname=["cbm_information"], as_dict=True)	
					except Exception as e:
						cbm.append({"cbm_information": 0}) 
						frappe.msgprint(_("Kindly contact your Admin support. Some Issue occure during request."))
		
				
					if(not cbm):
						cbm.append({"cbm_information": 0})

					i.update({"conversion_factor": v.conversion_factor})
					i.update({"uom": v.uom})
					i.update({"total_qty": float(v.conversion_factor * float(i.get("qty")))})
					i.update({"cbm_info": float(v.conversion_factor * float(i.get("qty")) * (float(cbm[0]['cbm_information']) if(cbm[0]['cbm_information'] != None) else 0.0) )})

