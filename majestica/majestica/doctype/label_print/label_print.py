# -*- coding: utf-8 -*-
# Copyright (c) 2019, sahil and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class LabelPrint(Document):
	pass

@frappe.whitelist()
def get_data(item_group):
        if(item_group):
                return frappe.db.sql("""select name, standard_rate as price from `tabItem` where item_group = {0} """.format(item_group), as_dict=True)
