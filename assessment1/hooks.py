app_name = "assessment1"
app_title = "assessment1"
app_publisher = "Paul Shaji"
app_description = "TechFab Industries erp"
app_email = "paulshaji1122@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "assessment1",
# 		"logo": "/assets/assessment1/logo.png",
# 		"title": "assessment1",
# 		"route": "/assessment1",
# 		"has_permission": "assessment1.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/assessment1/css/assessment1.css"
# app_include_js = "/assets/assessment1/js/assessment1.js"

# include js, css files in header of web template
# web_include_css = "/assets/assessment1/css/assessment1.css"
# web_include_js = "/assets/assessment1/js/assessment1.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "assessment1/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "assessment1/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "assessment1.utils.jinja_methods",
# 	"filters": "assessment1.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "assessment1.install.before_install"
# after_install = "assessment1.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "assessment1.uninstall.before_uninstall"
# after_uninstall = "assessment1.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "assessment1.utils.before_app_install"
# after_app_install = "assessment1.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "assessment1.utils.before_app_uninstall"
# after_app_uninstall = "assessment1.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "assessment1.notifications.get_notification_config"

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

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"assessment1.tasks.all"
# 	],
# 	"daily": [
# 		"assessment1.tasks.daily"
# 	],
# 	"hourly": [
# 		"assessment1.tasks.hourly"
# 	],
# 	"weekly": [
# 		"assessment1.tasks.weekly"
# 	],
# 	"monthly": [
# 		"assessment1.tasks.monthly"
# 	],
# }

doc_events = {
    "Sales Order": {
        "before_insert": "assessment1.api.sales_order.set_naming_series",
         "on_submit": "assessment1.api.procurement.create_material_request_on_so_submit"
    },
     "Work Order": {
        "on_submit": "assessment1.api.manufacturing.validate_material_availability"
    },
       "Salary Slip": {
        "before_save": "assessment1.api.hr.calculate_overtime_on_salary_slip"
    },
       "Payment Entry": {
        "on_submit": "assessment1.api.rewards.create_reward_log_on_payment"
    }
}

scheduler_events = {
    "daily": [
        "assessment1.api.asset_alerts.send_maintenance_alerts"
    ]
}

fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
             ["name", "in", ["Customer-custom_customer_type",
                             "Attendance-custom_overtime_hours"
                             ]]
        ]
    },
    {
        "doctype": "Number Card",
        "filters": [
               ["name", "in", [
                "Sales Orders-1",
                "Pending Purchases-1",
                "Production In Progress-1",
                "Production Completed-1",
                "Total Employees-2",
                "Total Reward Points"
            ]]
        ]
    },
    {
        "doctype": "Report",
        "filters": [
            ["name", "in", [
                "TechFab Management Report",
                "Department Wise Payroll Summary"
            ]]
        ]
    },
    {
        "doctype": "Workspace",
        "filters": [
            ["name", "=", "TechFab Dashboard"]
        ]
    }

]

# Testing
# -------

# before_tests = "assessment1.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "assessment1.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "assessment1.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["assessment1.utils.before_request"]
# after_request = ["assessment1.utils.after_request"]

# Job Events
# ----------
# before_job = ["assessment1.utils.before_job"]
# after_job = ["assessment1.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"assessment1.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

