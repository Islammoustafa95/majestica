# -*- coding: utf-8 -*-
# Copyright (c) 2020, sahil and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class InvoiceConsolidation(Document):
    def validate(self):
        self.update_values()

    def update_values(self):
        value = []
        for po in self.linked_invoices:
            for item in self.items:
                # data = frappe.db.sql("""select item_code, conversion_factor, uom from `tabPurchase Invoice Item` where item_code = %s and parent = %s """, (item.get(
                #     'item_code'), po.get('purchase_invoice')), as_dict=True)
                # if(data):
                #     value.append(data[0])
                child_doctype = "{} Item".format(po.reference_doctype)
                if po.reference_doctype == "Cap Stock Arrival":
                    child_doctype = "Stock Arrival Item"
                # frappe.throw(child_doctype)
                # data = frappe.db.sql("""select item_code, conversion_factor, uom from {} where item_code = '{}' and parent = '{}' 
                #     """.format(child_doctype,item.get('item_code'), po.get('purchase_invoice')), as_dict=True)
                conversion_factor = frappe.db.get_value(child_doctype, {"parent": po.purchase_invoice, "item_code": item.item_code}, "conversion_factor") or 1
                uom = frappe.db.get_value(child_doctype, {"parent": po.purchase_invoice, "item_code": item.item_code}, "uom")
                data = frappe._dict({"item_code": item.item_code, "conversion_factor": conversion_factor, "uom":uom})
                value.append(data)

        for i in self.items:
            for v in value:
                if(i.get("item_code") == v.item_code):
                    cbm = []
                    try:
                        cbm = frappe.db.get_values("Item", filters={"item_code": v.item_code}, fieldname=[
                                                   "cbm_information"], as_dict=True)
                    except Exception as e:
                        cbm.append({"cbm_information": 0})
                        frappe.msgprint(
                            _("Kindly contact your Admin support. Some Issue occure during request."))

                    if(not cbm):
                        cbm.append({"cbm_information": 0})

                    i.update({"conversion_factor": v.conversion_factor})
                    i.update({"uom": v.uom})
                    i.update(
                        {"total_qty": float(v.conversion_factor * float(i.get("qty")))})
                    i.update({"cbm_info": float(v.conversion_factor * float(i.get("qty")) * (float(
                        cbm[0]['cbm_information']) if(cbm[0]['cbm_information'] != None) else 0.0))})

        cbm_total = 0
        for item in self.items:
            cbm_total += item.cbm_info
        self.cbm_total = cbm_total


@frappe.whitelist()
def consolidate(source_names,doctype="Purchase Invoice", ptype=None):
    import json
    source_names = json.loads(source_names)
    # return source_names
    items = []
    temp_list = []
    child_doc = []
    for name in source_names:
        PI = frappe.get_doc(doctype, name)
        party = None
        if ptype:
            party = PI.get(frappe.scrub(ptype))
        tmep_chi = {
            "doctype": "Linked Invoice",
            "reference_doctype": doctype,
            "purchase_invoice": name,
            "ptype": ptype or "",
            "supplier": party
        }
        child_doc.append(tmep_chi)
        for item in PI.items:
            if item.item_code not in temp_list:
                temp_item = {
                    "doctype": "Goods Item",
                    "item_code": item.item_code,
                    "qty": item.qty,
                    "uom": item.uom,
                    "conversion_factor": item.conversion_factor,
                    "total_qty": item.qty
                }
                items.append(temp_item)
                temp_list.append(item.item_code)
            else:
                for index in items:
                    if index["item_code"] == item.item_code and index["uom"]== item.uom:
                        index["qty"] = int(index["qty"])+item.qty
                        index["total_qty"] = int(
                            index["total_qty"])+item.qty

    doc = frappe.get_doc({
        "doctype": "Invoice Consolidation",
        "linked_invoices": child_doc,
        "items": items
    })
    doc.save()
    return doc
