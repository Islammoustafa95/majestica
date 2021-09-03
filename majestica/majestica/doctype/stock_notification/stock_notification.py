# -*- coding: utf-8 -*-
# Copyright (c) 2019, sahil and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.utilities.product import get_qty_in_stock

class StockNotification(Document):
	pass

@frappe.whitelist()
def create_stock_notification(item, customer, item_route):
    stock_notification = frappe.new_doc("Stock Notification")
    stock_notification.update({
        "item_name": item,
        "customer_name": customer,
        "item_route": item_route
    })
    stock_notification.insert(ignore_permissions=True, ignore_mandatory=True)

@frappe.whitelist()
def check_stock_status():
    stock_notification_list = frappe.get_all('Stock Notification', filters={'stock_status': 'Out of Stock', 'email_notify': 0}, fields=['name', 'item_name'])
    for stock_notification in stock_notification_list:
        cur_notification = frappe.get_doc('Stock Notification', stock_notification['name'])
        stock_status = get_qty_in_stock(stock_notification['item_name'], "website_warehouse")
        if stock_status[0]['in_stock_item'] == 1:
            cur_notification.update({'stock_status': 'In Stock', 'email_notify': 1})
            cur_notification.save(ignore_permissions=True)
    return("Operation Completed")

@frappe.whitelist()
def update_web_status():
    stock_notification_list = frappe.get_all('Stock Notification', filters={'stock_status': 'In Stock', 'website_notify': 0}, fields=['name', 'item_name'])
    for stock_notification in stock_notification_list:
        cur_notification = frappe.get_doc('Stock Notification', stock_notification['name'])
        cur_notification.update({'website_notify': 1})
        cur_notification.save(ignore_permissions=True)
    return("Operation Completed")
