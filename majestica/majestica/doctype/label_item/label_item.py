# -*- coding: utf-8 -*-
# Copyright (c) 2019, sahil and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class LabelItem(Document):
	@frappe.whitelist()
	def set_barcode_item(self):
		frappe.msgprint(str(self));
