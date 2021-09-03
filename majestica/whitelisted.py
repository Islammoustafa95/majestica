from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import frappe.utils
from frappe.utils import flt
import collections
from frappe import _, msgprint
import json

@frappe.whitelist()
def before_invoice(items, user):
    try:
        data = json.loads(items)
        item = []
        amount = []
        final_data = []
        for i in data:
            item.append(i["item_code"])
            amount.append(i["amount"])

        final_data.append({"name": "New Invoice", "customer": "", "discount_amount": 0, "grand_total": sum(amount), "outstanding_amount": "", "amount": round(sum(amount),2), "items":'<br/><br/>'.join(map(str, item))})

        frappe.publish_realtime(user, message=final_data)
    except Exception as e:
        frappe.msgprint(e)
    

@frappe.whitelist()
def get_po_items(data):
	item = []
	if(data):
		for d in eval(data):
			item_data = frappe.db.sql("""select item_code, item_name, qty from `tabPurchase Order Item` where parent = %s """,(d), as_dict=True)
			if(item_data):
				item.append(item_data)

	if(item):
		item = sum(item, [])
		value = collections.Counter()
		for i in item:
			value[i['item_code']] += int(i['qty'])

		final_value = ([{"item_code":n,"qty":str(v)} for n,v in value.items()])
		return final_value


@frappe.whitelist()
def get_item(barcode):
	if(barcode):
		data = frappe.db.sql("""select parent from `tabItem Barcodes` where barcode = %s  """,barcode, as_dict=True);
		return data

@frappe.whitelist()
def combine_arrial(name):
	if(name):
		items = []
		for n in eval(name):
			item = frappe.db.sql("""select item_code, qty from `tabFinal Arrival Items` where docstatus != 2 and parent = %s """, n, as_dict=True)
		
			if(item):
				for i in item:
					items.append({"item_code": i.item_code, "qty": i.qty})

		if(items):
			doc = frappe.new_doc("Stock Arrival")
			doc.supplier_info = "Combine Doc "+str(name)
			doc.enable = 1
			doc.date = frappe.utils.nowdate()

			for j in items:
				doc.append("items", {
					"item_code": j.get("item_code"),
					"qty": j.get("qty"),
					"uom_conversion_factor": 1,
					"received_qty": 1
				})

			doc.save(ignore_permissions=True)



@frappe.whitelist()
def get_item_data(barcode):
	if(barcode):
		data = frappe.db.sql("""select parent from `tabItem Barcodes` where barcode = %s """, (barcode), as_dict=True)

		if(data):
			return data
		else:
			frappe.msgprint(_("Item not found with the given barcode.", title="Item Not Found"))


@frappe.whitelist()
def pos(name):
        try:
                doc = frappe.get_doc("Sales Invoice", {"name":name})
                data = []
                
                item = []
                items = []
                item = frappe.db.sql("""select item_code from `tabSales Invoice Item` where parent = %s """,(name), as_dict=True)
                if(item):
                        for i in item:
                                items.append(i.item_code)
                data.append({"name": doc.name, "customer": doc.customer, "discount_amount": doc.discount_amount, "grand_total": doc.grand_total, "outstanding_amount": doc.outstanding_amount, "amount": doc.total, "items":'<br/><br/>'.join(map(str, items))})

                frappe.publish_realtime(doc.owner, message=data)
        except Exception as e:
                frappe.msgprint(_("{0}").format(e))


@frappe.whitelist()
def save_rating(invoice, customer, quality_of_service, quality_of_products, quality_of_cleanliness,age_group):
    try:
        doc = frappe.new_doc("Customer Rating")
        doc.sales_invoice = invoice
        doc.customer = customer
        doc.age_group=age_group
        doc.quality_of_service = quality_of_service
        doc.quality_of_products = quality_of_products
        doc.quality_of_cleanliness = quality_of_cleanliness
        doc.save(ignore_permissions=True)
    except Exception as e:
        frappe.msgprint(e)
