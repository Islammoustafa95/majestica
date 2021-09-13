# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "majestica"
app_title = "Majestica"
app_publisher = "sahil"
app_description = "Erpnext Customization"
app_icon = "octicon octicon-file-directory"
app_color = "blue"
app_email = "sahil19893@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/majestica/css/majestica.css"
# app_include_js = "/assets/majestica/js/majestica.js"
app_include_js = "/assets/majestica/js/fullsize.js"
app_include_css = "assets/majestica/css/custom.css"
# include js, css files in header of web template
web_include_css = [
	"/assets/majestica/css/majestica.min.js"
]
# web_include_js = "/assets/majestica/js/majestica.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "majestica.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "majestica.install.before_install"
# after_install = "majestica.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "majestica.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	# "all": [
	# 	"majestica.tasks.all"
	# ],
	# "daily": [
	# 	"majestica.tasks.daily"
	# ],
	#"hourly": [
	#	"erpnext.stock.doctype.item.item.sync_with_woocommerce"
	#],
	# "weekly": [
	# 	"majestica.tasks.weekly"
	# ]
	# "monthly": [
	# 	"majestica.tasks.monthly"
	# ]
}

# Testing
# -------

# before_tests = "majestica.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "majestica.event.get_events"
# }
fixtures = ['Report', 'Role Profile', 'Role', 'Custom Field', 'Custom Script', 'Property Setter', 'Workflow', 'Workflow State', 'Workflow Action', 'Item']

doctype_list_js = {
	"Purchase Order":"public/js/puchase_order_list.js"
}

doctype_js = {
	"Sales Invoice": "public/js/controller/sales_invoice.js"
}
