# Copyright (c) 2018, sahil and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, cstr, flt, fmt_money
from frappe import _, _dict
from erpnext.accounts.utils import get_account_currency
#from majestica.majestica.report.majestica_accounts_receivable.majestica_accounts_receivable import ReceivablePayableReport
from erpnext.accounts.report.accounts_receivable.accounts_receivable import ReceivablePayableReport
from datetime import datetime
from frappe import _, msgprint

def execute(filters=None):
	account_details = {}

	if filters and filters.get('print_in_account_currency') and \
		not filters.get('account'):
		frappe.throw(_("Select an account to print in account currency"))

	for acc in frappe.db.sql("""select name, is_group from tabAccount""", as_dict=1):
		account_details.setdefault(acc.name, acc)

	validate_filters(filters, account_details)

	validate_party(filters)

	filters = set_account_currency(filters)

	columns = get_columns(filters)

	res = get_result(filters, account_details)

	args = {
		"party_type": "Customer",
		"naming_by": ["Selling Settings", "cust_master_name"],
	}
	column2, res2, x, y = ReceivablePayableReport(filters).run(args)

	col = []
	count = 0
	for c in column2:
		count += 1
		if(count <= 15):
			col.append(c)

	final_data = []

	key = ['Posting Date', 'Customer', 'Voucher Type', 'Voucher No', 'Due Date', 'Invoiced Amount', 'Paid Amount', 'Credit Note', 'Outstanding Amount', 'Age (Days)', '0-30', '31-60', '61-90', '91-Above', 'Currency']

	for d in res2:
		if(filters.get("party") in d):
			count = 0
			data = ""
			new_data = []
			for i in d:
				count += 1
				if(count <= 15):
					new_data.append(i)
			data = dict(zip(key, new_data))
			final_data.append(data)

	data = res
	frappe.msgprint(_("{0}, {1}").format(len(final_data), len(data)))
	if(final_data):
		for d in range(0, len(final_data)):
			data[d+1].update(final_data[d])

	print(final_data)

	print(data)
	res = res+final_data
	return columns, data

def validate_filters(filters, account_details):
	if not filters.get('company'):
		frappe.throw(_('{0} is mandatory').format(_('Company')))

	if filters.get("account") and not account_details.get(filters.account):
		frappe.throw(_("Account {0} does not exists").format(filters.account))

	if filters.get("account") and filters.get("group_by_account") \
			and account_details[filters.account].is_group == 0:
		frappe.throw(_("Can not filter based on Account, if grouped by Account"))

	if filters.get("voucher_no") and filters.get("group_by_voucher"):
		frappe.throw(_("Can not filter based on Voucher No, if grouped by Voucher"))

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))


def validate_party(filters):
	party_type, party = filters.get("party_type"), filters.get("party")

	if party:
		if not party_type:
			frappe.throw(_("To filter based on Party, select Party Type first"))
		elif not frappe.db.exists(party_type, party):
			frappe.throw(_("Invalid {0}: {1}").format(party_type, party))

def set_account_currency(filters):
	if not (filters.get("account") or filters.get("party")):
		return filters
	else:
		filters["company_currency"] = frappe.db.get_value("Company", filters.company, "default_currency")
		account_currency = None

		if filters.get("account"):
			account_currency = get_account_currency(filters.account)
		elif filters.get("party"):
			gle_currency = frappe.db.get_value("GL Entry", {"party_type": filters.party_type,
				"party": filters.party, "company": filters.company}, "account_currency")
			if gle_currency:
				account_currency = gle_currency
			else:
				account_currency = (None if filters.party_type in ["Employee", "Student", "Shareholder", "Member"] else
					frappe.db.get_value(filters.party_type, filters.party, "default_currency"))

		filters["account_currency"] = account_currency or filters.company_currency

		if filters.account_currency != filters.company_currency:
			filters["show_in_account_currency"] = 1

		return filters

def get_result(filters, account_details):
	gl_entries = get_gl_entries(filters)

	data = get_data_with_opening_closing(filters, account_details, gl_entries)

	result = get_result_as_list(data, filters)

	return result

def get_gl_entries(filters):
	select_fields = """, sum(debit_in_account_currency) as debit_in_account_currency,
		sum(credit_in_account_currency) as credit_in_account_currency""" \
		if filters.get("show_in_account_currency") else ""

	group_by_condition = "group by voucher_type, voucher_no, account, cost_center" \
		if filters.get("group_by_voucher") else "group by name"

	gl_entries = frappe.db.sql("""
		select
			posting_date, account, party_type, party,
			sum(debit) as debit, sum(credit) as credit,
			voucher_type, voucher_no, cost_center, project,
			against_voucher_type, against_voucher,
			remarks, against, is_opening {select_fields}
		from `tabGL Entry`
		where company=%(company)s {conditions}
		{group_by_condition}
		order by posting_date, account"""\
		.format(select_fields=select_fields, conditions=get_conditions(filters),
			group_by_condition=group_by_condition), filters, as_dict=1)

	return gl_entries

def get_conditions(filters):
	conditions = []
	if filters.get("account"):
		lft, rgt = frappe.db.get_value("Account", filters["account"], ["lft", "rgt"])
		conditions.append("""account in (select name from tabAccount
			where lft>=%s and rgt<=%s and docstatus<2)""" % (lft, rgt))

	if filters.get("voucher_no"):
		conditions.append("voucher_no=%(voucher_no)s")

	if filters.get("party_type"):
		conditions.append("party_type=%(party_type)s")

	if filters.get("party"):
		conditions.append("party=%(party)s")

	if not (filters.get("account") or filters.get("party") or filters.get("group_by_account")):
		conditions.append("posting_date >=%(from_date)s")

	if filters.get("project"):
		conditions.append("project=%(project)s")

	from frappe.desk.reportview import build_match_conditions
	match_conditions = build_match_conditions("GL Entry")
	if match_conditions: conditions.append(match_conditions)

	return "and {}".format(" and ".join(conditions)) if conditions else ""

def get_data_with_opening_closing(filters, account_details, gl_entries):
	data = []
	gle_map = initialize_gle_map(gl_entries)

	totals, entries = get_accountwise_gle(filters, gl_entries, gle_map)

	# Opening for filtered account
	data.append(totals.opening)

	if filters.get("group_by_account"):
		for acc, acc_dict in gle_map.items():
			if acc_dict.entries:
				# opening
				data.append({})
				data.append(acc_dict.totals.opening)

				data += acc_dict.entries

				# totals
				data.append(acc_dict.totals.total)

				# closing
				data.append(acc_dict.totals.closing)
		data.append({})

	else:
		data += entries

	# totals
	data.append(totals.total)

	# closing
	data.append(totals.closing)

	return data

def get_totals_dict():
	def _get_debit_credit_dict(label):
		return _dict(
			account = "'{0}'".format(label),
			debit = 0.0,
			credit = 0.0,
			debit_in_account_currency = 0.0,
			credit_in_account_currency = 0.0
		)
	return _dict(
		opening = _get_debit_credit_dict(_('Opening')),
		total = _get_debit_credit_dict(_('Total')),
		closing = _get_debit_credit_dict(_('Closing (Opening + Total)'))
	)

def initialize_gle_map(gl_entries):
	gle_map = frappe._dict()
	for gle in gl_entries:
		gle_map.setdefault(gle.account, _dict(totals = get_totals_dict(), entries = []))
	return gle_map

def get_accountwise_gle(filters, gl_entries, gle_map):
	totals = get_totals_dict()
	entries = []

	def update_value_in_dict(data, key, gle):
		data[key].debit += flt(gle.debit)
		data[key].credit += flt(gle.credit)

		data[key].debit_in_account_currency += flt(gle.debit_in_account_currency)
		data[key].credit_in_account_currency += flt(gle.credit_in_account_currency)


	from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
	for gle in gl_entries:
		if gle.posting_date < from_date or cstr(gle.is_opening) == "Yes":
			update_value_in_dict(gle_map[gle.account].totals, 'opening', gle)
			update_value_in_dict(totals, 'opening', gle)
			
			update_value_in_dict(gle_map[gle.account].totals, 'closing', gle)
			update_value_in_dict(totals, 'closing', gle)

		elif gle.posting_date <= to_date:
			update_value_in_dict(gle_map[gle.account].totals, 'total', gle)
			update_value_in_dict(totals, 'total', gle)
			if filters.get("group_by_account"):
				gle_map[gle.account].entries.append(gle)
			else:
				entries.append(gle)

			update_value_in_dict(gle_map[gle.account].totals, 'closing', gle)
			update_value_in_dict(totals, 'closing', gle)

	return totals, entries

def get_result_as_list(data, filters):
	balance, balance_in_account_currency = 0, 0
	inv_details = get_supplier_invoice_details()

	for d in data:
		if not d.get('posting_date'):
			balance, balance_in_account_currency = 0, 0

		balance = get_balance(d, balance, 'debit', 'credit')
		d['balance'] = balance

		if filters.get("show_in_account_currency"):
			balance_in_account_currency = get_balance(d, balance_in_account_currency,
				'debit_in_account_currency', 'credit_in_account_currency')
			d['balance_in_account_currency'] = balance_in_account_currency
		else:
			d['debit_in_account_currency'] = d.get('debit', 0)
			d['credit_in_account_currency'] = d.get('credit', 0)
			d['balance_in_account_currency'] = d.get('balance')

		d['account_currency'] = filters.account_currency
		d['bill_no'] = inv_details.get(d.get('against_voucher'), '')

	return data

def get_supplier_invoice_details():
	inv_details = {}
	for d in frappe.db.sql(""" select name, bill_no from `tabPurchase Invoice`
		where docstatus = 1 and bill_no is not null and bill_no != '' """, as_dict=1):
		inv_details[d.name] = d.bill_no

	return inv_details

def get_balance(row, balance, debit_field, credit_field):
	balance += (row.get(debit_field, 0) -  row.get(credit_field, 0))

	return balance

def get_columns(filters):
	columns = [
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 90
		},
		{
			"label": _("Account"),
			"fieldname": "account",
			"fieldtype": "Link",
			"options": "Account",
			"width": 180
		},
		{
			"label": _("Debit"),
			"fieldname": "debit",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"label": _("Credit"),
			"fieldname": "credit",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"label": _("Balance (Dr - Cr)"),
			"fieldname": "balance",
			"fieldtype": "Float",
			"width": 130
		}
	]

	if filters.get("show_in_account_currency"):
		columns.extend([
			{
				"label": _("Debit") + " (" + filters.account_currency + ")",
				"fieldname": "debit_in_account_currency",
				"fieldtype": "Float",
				"width": 100
			},
			{
				"label": _("Credit") + " (" + filters.account_currency + ")",
				"fieldname": "credit_in_account_currency",
				"fieldtype": "Float",
				"width": 100
			},
			{
				"label": _("Balance") + " (" + filters.account_currency + ")",
				"fieldname": "balance_in_account_currency",
				"fieldtype": "Data",
				"width": 100
			}
		])

	columns.extend([
		{
			"label": _("Voucher Type"),
			"fieldname": "voucher_type",
			"width": 120
		},
		{
			"label": _("Voucher No"),
			"fieldname": "voucher_no",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 180
		},
		{
			"label": _("Against Account"),
			"fieldname": "against",
			"width": 120
		},
		{
			"label": _("Party Type"),
			"fieldname": "party_type",
			"width": 100
		},
		{
			"label": _("Party"),
			"fieldname": "party",
			"width": 100
		},
		{
			"label": _("Project"),
			"options": "Project",
			"fieldname": "project",
			"width": 100
		},
		{
			"label": _("Cost Center"),
			"options": "Cost Center",
			"fieldname": "cost_center",
			"width": 100
		},
		{
			"label": _("Against Voucher Type"),
			"fieldname": "against_voucher_type",
			"width": 100
		},
		{
			"label": _("Against Voucher"),
			"fieldname": "against_voucher",
			"fieldtype": "Dynamic Link",
			"options": "against_voucher_type",
			"width": 100
		},
		{
			"label": _("Supplier Invoice No"),
			"fieldname": "bill_no",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Remarks"),
			"fieldname": "remarks",
			"width": 400
		},
		{
			"label": _("Customer"),
			"field_name": "customer",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Voucher No"),
			"field_name": "voucher_no",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Due Date"),
			"field_name": "due_date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"label": _("Invoiced Amount"),
			"field_name": "invoice_amount",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Voucher Type"),
			"field_name": "voucher_type",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("91-Above"),
			"field_name": "amount4",
			"fieldtype": "Float",
			"width": 100	
		},
		{
			"label": _("31-60"),
			"field_name": "amount3",
			"fieldtype": "Data",
			"width": 100
		},
		{
                        "label": _("Age (Days)"),
                        "field_name": "age",
                        "fieldtype": "Data",
                        "width": 100
                },
		{
                        "label": _("Currency"),
                        "field_name": "currency",
                        "fieldtype": "Data",
                        "width": 100
                },
		{
                        "label": _("Outstanding Amount"),
                        "field_name": "outstanding_amount",
                        "fieldtype": "Data",
                        "width": 100
                },
		{
                        "label": _("Credit Note"),
                        "field_name": "credit_note",
                        "fieldtype": "Data",
                        "width": 100
                },
		{
                        "label": _("0-30"),
                        "field_name": "amount1",
                        "fieldtype": "Float",
                        "width": 100
                },
		{
                        "label": _("Paid Amount"),
                        "field_name": "paid_amount",
                        "fieldtype": "Data",
                        "width": 100
                },
		{
                        "label": _("61-90"),
                        "field_name": "amount2",
                        "fieldtype": "Float",
                        "width": 100
                },
		{
                        "label": _("Posting Date"),
                        "field_name": "posting_date",
                        "fieldtype": "Date",
                        "width": 100
                },
		{
			"label": _("Customer Address"),
			"fieldtype": "Short Text",
			"field_name": "customer_address",
			"width": 200
		}
	])

	return columns
