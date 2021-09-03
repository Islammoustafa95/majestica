# -*- coding: utf-8 -*-
# Copyright (c) 2019, sahil and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Voucher(Document):
	pass

@frappe.whitelist()
def bulk_voucher_generate(amount, total):
    for v in range(int(total)):
        v = frappe.new_doc("Voucher")
        v.update({
            "amount": amount
        })
        v.insert()
    return("Bulk Generation Completed.")

