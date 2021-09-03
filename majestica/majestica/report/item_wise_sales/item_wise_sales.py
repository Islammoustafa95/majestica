from __future__ import unicode_literals
import frappe
from frappe import _
from collections import defaultdict
from frappe.utils import flt, cint, getdate, now, date_diff
import operator
import collections
import itertools

def execute(filters=None):
	if not filters:
		filters = {}
	filters["report_mode"] ="ItemWise"
	report={"CategoryWise":'item_group', "Sub-CategoryWise":'sub_category', 'ItemWise':'item_code'}
	columns = get_column(filters)
	conditions = get_conditions(filters)
	opening_closing = get_data(conditions, filters)
	report_type = report.get(filters.get("report_mode"))
	data = []
	grouped = collections.defaultdict(list)
	result = {}
	for (item,warehouse) in opening_closing:
		row = {}
		qty_dict = opening_closing[(item,warehouse)]
		if qty_dict.sale > 0:
			qty_dict.sale = -qty_dict.sale
		else:
			qty_dict.sale = abs(qty_dict.sale)
		if result.get(qty_dict.item_code):
			result[qty_dict.item_code]["sale"] += qty_dict.sale
			# result[qty_dict.item_code]["closing"] += qty_dict.closing
			# divide_by = result.get(qty_dict.item_code).get("closing")
			# if not divide_by: divide_by = 1.0
			# result[qty_dict.item_code]["valuation_rate"] = result.get(qty_dict.item_code).get("bal_val")/divide_by
		else:
			row['item_code'] = qty_dict.item_code
			row['sale'] = qty_dict.sale
			
			#row['qty'] =  frappe.db.get_value("Item Expiry", {"parent": qty_dict.item_code}, "qty")
			#row['item_expiry'] = frappe.db.get_value("Item Expiry", {"parent": qty_dict.item_code}, "date")

			row['item_expiry_qty'] = get_open_material_request(qty_dict.item_code)

			result[qty_dict.item_code] = row
	for d,i in result.items():
		data.append(i)

	return columns, data



def get_column(filters):
	report={"CategoryWise":'item_group', "Sub-CategoryWise":'sub_category', 'ItemWise':'item_code'}
	gr = report.get(filters.get("report_mode"))
	columns = [
		# {"fieldname": "item_code", "label": _("Item Code"), "width": 150},
		{"fieldname": "item_code", "label": _("Item Code"), "width": 200},
		# {"fieldname": "item_group", "label": _("Item Group"), "width": 150},
		# {"fieldname": "warehouse", "label": _("Warehouse"), "width": 150},
		# {"fieldname": "stock_uom", "label": _("UOM"), "width": 150, "fieldtype": ""},
		# {"fieldname": "closing", "label": _("Balance Qty"), "width": 150, "fieldtype": "Float"},
		# {"fieldname": "adjustment", "label": _("Adjustment"), "width": 150},
		# {"fieldname": "bal_val", "label": _("Balance Value"), "width": 150, "fieldtype": "Float"},
		# {"fieldname": "valuation_rate", "label": _("Valuation Rate"), "width": 150, "fieldtype": "Float"},
		{"fieldname": "sale", "label": _("Sale"), "width": 150, "fieldtype": "Float"},
		# {"fieldname": "qty", "label": _("Qty"), "width": 150, "fieldtype": "Float"},
		# {"fieldname": "item_expiry", "label": _("Item Expiry"), "width": 150, "fieldtype": "Date"},
		{"fieldname": "item_expiry_qty", "label": _("Item Expiry Qty  "), "width": 250, "fieldtype": "Data"},

	]
	# columns[0]['fieldtype']='Link'
	# columns[0]['options']='Item'
	return columns

def get_data(conditions, filters):
	from_date = frappe.utils.getdate(filters.get("from_date"))
	to_date = frappe.utils.getdate(filters.get("to_date"))
	report={"CategoryWise":'item_group', "Sub-CategoryWise":'sub_category', 'ItemWise':'item_code'}
	gr = report.get(filters.get("report_mode"))
	item=[]
	iwb_map = {}
	data = frappe.db.sql("""
        select i.item_code as item_code, i.item_group as item_group,   i.item_name, sle.warehouse,
        sle.actual_qty as actual_qty, sle.posting_date as posting_date, 
        sle.voucher_type as voucher_type, sle.qty_after_transaction as qty_after_transaction, sle.name as name,
        sle.stock_value_difference, i.stock_uom, sle.valuation_rate
         from `tabStock Ledger Entry` sle force index (posting_sort_index)
        inner join `tabItem` i on sle.item_code = i.item_code 
        where i.disabled = 0 and sle.docstatus < 2
        and sle.posting_date <= '{to_date}' {conditions}
        order by sle.posting_date, sle.posting_time, sle.creation, sle.actual_qty
		""".format(to_date=to_date, conditions=conditions), as_dict=1)
	for d in data:
		report_type = report.get(filters.get("report_mode"))
		key = (d.get("item_code"), d.get("warehouse"))
		if key not in iwb_map:
			iwb_map[key] = frappe._dict({
				"item_code": d.item_code, "item_name": d.item_name,
				"item_group": d.item_group or "None", "warehouse": d.warehouse or "None",
				"stock_uom": d.stock_uom,
				"opening": 0.0, "closing": 0.0,
				"receipt": 0.0, "transfer": 0.0,
				"sale": 0.0, "adjustment": 0.0,
				"bal_val": 0.0,

			})
		qty_dict = iwb_map[key]
		qty_diff=0.0
		if d.voucher_type == "Stock Reconciliation":
			qty_diff = flt(d.qty_after_transaction) - qty_dict.closing
		else:
			qty_diff = flt(d.actual_qty)

		value_diff = flt(d.stock_value_difference)

		if d.posting_date >= from_date and d.posting_date <= to_date:
			if d.voucher_type == "Sales Invoice":
				qty_dict.sale += qty_diff

		# if d.posting_date < from_date:
		# 	qty_dict.opening += qty_diff
		qty_dict.closing += qty_diff
		qty_dict.bal_val += value_diff
		qty_dict.valuation_rate = d.valuation_rate
	return iwb_map

def get_conditions(filters):
	conditions = ""
	if filters.get("item"):
		conditions += " and sle.item_code = '{}'".format(filters.get("item"))
	if filters.get("item_group"):
		conditions += " and i.item_group = '{}'".format(filters.get("item_group"))
	if filters.get("warehouse"):
		conditions += " and sle.warehouse = '{}'".format(filters.get("warehouse"))
	return conditions

def get_sold_qty(item_code, date, warehouse = None):
	qty = 0
	cond = ""
	if warehouse:
		cond += " and p.warehouse = '{}'".format(warehouse)
	data = frappe.db.sql("""select sum(c.sales) from `tabVan Salesman Load Item` c inner join 
		`tabVan Salesman Load` p on p.name = c.parent where p.docstatus = 1 and 
		p.posting_date >= '{}' and c.item_code = '{}' {}
		""".format(date,item_code, cond))
	if data: qty = data[0][0]
	if not qty: qty = p
	return qty


def get_qty(item):
	#data = frappe.db.get_value("Item Expiry", {"parent": item}, "qty")
	data = frappe.db.sql("""select  e.qty from `tabItem`i  inner join 
		`tabItem Expiry`  e on i.name = e.parent where i.docstatus=1 and  i.item_code = %s """,(item))

	return data

def get_expire_qty(item):
	material_requests = ""
	data = frappe.db.sql("""select e.date, e.qty from `tabItem` i inner join 
		`tabItem Expiry` e on  e.parent = i.name where i.docstatus=1 and i.item_code = %s""",(item))
	for d in data:
		material_requests += d[0]+" ("+str(d[1])+"), "
	#frappe.msgprint(str(material_requests))
	return material_requests




def get_open_material_request(item):
	material_requests = ""
	data = frappe.db.sql("""select c.date, c.qty from `tabItem` p inner join 
		`tabItem Expiry` c on c.parent = p.name where  p.item_code = %s""",(item))
	for d in data:
		material_requests += str(d[0])+" ("+str(d[1])+"), "
	return material_requests
