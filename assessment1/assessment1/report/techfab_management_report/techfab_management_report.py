import frappe
from frappe.utils import nowdate, get_first_day, get_last_day, getdate, add_days


def execute(filters=None):
    columns = get_columns()
    data = get_data()
    return columns, data


def get_columns():
    return [
        {
            "label": "Metric",
            "fieldname": "metric",
            "fieldtype": "Data",
            "width": 280
        },
        {
            "label": "Value",
            "fieldname": "value",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "Details",
            "fieldname": "details",
            "fieldtype": "Data",
            "width": 350
        },
    ]


def get_data():
    today = getdate(nowdate())
    first_day = get_first_day(today)
    last_day = get_last_day(today)
    data = []

    # Section 1 — Sales Orders
    data.append({
        "metric": "── SALES ──",
        "value": "",
        "details": ""
    })
    total_so = frappe.db.count("Sales Order", {"docstatus": 1})
    pending_so = frappe.db.count("Sales Order", {
        "docstatus": 1,
        "status": ["in", ["To Deliver and Bill", "To Bill", "To Deliver"]]
    })
    data.append({
        "metric": "Total Sales Orders",
        "value": total_so,
        "details": f"{pending_so} pending delivery or billing"
    })

    # Section 2 — Procurement
    data.append({"metric": "── PROCUREMENT ──", "value": "", "details": ""})
    pending_mr = frappe.db.count("Material Request", {"docstatus": 1})
    pending_po = frappe.db.count("Purchase Order", {
        "docstatus": 1,
        "status": ["in", ["To Receive and Bill", "To Receive", "To Bill"]]
    })
    data.append({
        "metric": "Pending Material Requests",
        "value": pending_mr,
        "details": f"{pending_po} open Purchase Orders"
    })

    # Section 3 — Production
    data.append({"metric": "── PRODUCTION ──", "value": "", "details": ""})
    planned = frappe.db.count("Work Order", {"docstatus": 1, "status": "Not Started"})
    in_process = frappe.db.count("Work Order", {"docstatus": 1, "status": "In Process"})
    completed = frappe.db.count("Work Order", {"docstatus": 1, "status": "Completed"})
    data.append({"metric": "Planned", "value": planned, "details": "Not yet started"})
    data.append({"metric": "In Progress", "value": in_process, "details": "Currently in production"})
    data.append({"metric": "Completed", "value": completed, "details": "Production done"})

    # Section 4 — Assets
    data.append({"metric": "── ASSETS ──", "value": "", "details": ""})
    alert_window = add_days(today, 30)
    due_assets = frappe.db.sql("""
        SELECT COUNT(*)
        FROM `tabAsset Maintenance Task` amt
        INNER JOIN `tabAsset Maintenance` am ON am.name = amt.parent
        WHERE amt.next_due_date BETWEEN %s AND %s
    """, (today, alert_window))[0][0]
    data.append({
        "metric": "Assets Due for Maintenance",
        "value": due_assets,
        "details": "Due within next 30 days"
    })

    # Section 5 — Employees
    data.append({"metric": "── HR ──", "value": "", "details": ""})
    total_emp = frappe.db.count("Employee", {"status": "Active"})
    departments = frappe.db.sql("""
        SELECT department, COUNT(name) as cnt
        FROM `tabEmployee`
        WHERE status = 'Active' AND department IS NOT NULL
        GROUP BY department
    """, as_dict=True)
    dept_str = " | ".join([f"{d.department}: {d.cnt}" for d in departments])
    data.append({
        "metric": "Total Active Employees",
        "value": total_emp,
        "details": dept_str
    })

    # Section 6 — Payroll
    payroll_cost = frappe.db.sql("""
        SELECT COALESCE(SUM(net_pay), 0)
        FROM `tabSalary Slip`
        WHERE docstatus = 1
        AND start_date >= %s
        AND end_date <= %s
    """, (first_day, last_day))[0][0] or 0
    data.append({
        "metric": "Monthly Payroll Cost",
        "value": f"INR {payroll_cost:,.2f}",
        "details": f"For {first_day.strftime('%B %Y')}"
    })

    # Department-wise payroll
    dept_payroll = frappe.db.sql("""
        SELECT e.department, COALESCE(SUM(ss.net_pay), 0) as total
        FROM `tabSalary Slip` ss
        LEFT JOIN `tabEmployee` e ON e.name = ss.employee
        WHERE ss.docstatus = 1
        AND ss.start_date >= %s
        AND ss.end_date <= %s
        GROUP BY e.department
    """, (first_day, last_day), as_dict=True)
    for d in dept_payroll:
        data.append({
            "metric": f"  {d.department or 'Unassigned'}",
            "value": f"INR {d.total:,.2f}",
            "details": "Department payroll"
        })

    # Section 7 — Reward Points
    data.append({"metric": "── REWARD POINTS ──", "value": "", "details": ""})
    reward_data = frappe.db.sql("""
        SELECT sales_person, SUM(points_earned) as total_points
        FROM `tabSalesperson Reward Log`
        GROUP BY sales_person
        ORDER BY total_points DESC
    """, as_dict=True)
    if reward_data:
        for r in reward_data:
            data.append({
                "metric": r.sales_person,
                "value": int(r.total_points),
                "details": "Cumulative reward points"
            })
    else:
        data.append({
            "metric": "No reward points yet",
            "value": 0,
            "details": ""
        })

    return data
