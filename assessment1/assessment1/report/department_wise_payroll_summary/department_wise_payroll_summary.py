import frappe
from frappe.utils import getdate


def execute(filters=None):
    filters = filters or {}
    validate_filters(filters)
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def validate_filters(filters):
    if not filters.get("from_date") or not filters.get("to_date"):
        frappe.throw("Please set both From Date and To Date.")
    if getdate(filters["from_date"]) > getdate(filters["to_date"]):
        frappe.throw("From Date cannot be after To Date.")


def get_columns():
    return [
        {
            "label": "Department",
            "fieldname": "department",
            "fieldtype": "Link",
            "options": "Department",
            "width": 200,
        },
        {
            "label": "Employees",
            "fieldname": "employee_count",
            "fieldtype": "Int",
            "width": 110,
        },
        {
            "label": "Total Basic (INR)",
            "fieldname": "total_basic",
            "fieldtype": "Currency",
            "width": 160,
        },
        {
            "label": "Total Overtime (INR)",
            "fieldname": "total_overtime",
            "fieldtype": "Currency",
            "width": 170,
        },
        {
            "label": "Total Deductions (INR)",
            "fieldname": "total_deductions",
            "fieldtype": "Currency",
            "width": 180,
        },
        {
            "label": "Net Pay (INR)",
            "fieldname": "net_pay",
            "fieldtype": "Currency",
            "width": 150,
        },
    ]


def get_data(filters):
    from_date = filters["from_date"]
    to_date = filters["to_date"]

    # Submitted salary slips in the date range, grouped by department
    dept_rows = frappe.db.sql("""
        SELECT
            COALESCE(e.department, 'Unassigned') AS department,
            COUNT(DISTINCT ss.employee)           AS employee_count,
            COALESCE(SUM(ss.gross_pay), 0)        AS total_gross,
            COALESCE(SUM(ss.total_deduction), 0)  AS total_deductions,
            COALESCE(SUM(ss.net_pay), 0)          AS net_pay
        FROM `tabSalary Slip` ss
        LEFT JOIN `tabEmployee` e ON e.name = ss.employee
        WHERE ss.docstatus = 1
          AND ss.start_date >= %(from_date)s
          AND ss.end_date   <= %(to_date)s
        GROUP BY e.department
        ORDER BY e.department
    """, {"from_date": from_date, "to_date": to_date}, as_dict=True)

    if not dept_rows:
        return []

    # Fetch per-component totals (Basic, Overtime) in one query
    component_rows = frappe.db.sql("""
        SELECT
            COALESCE(e.department, 'Unassigned') AS department,
            ssd.salary_component,
            COALESCE(SUM(ssd.amount), 0)         AS total_amount
        FROM `tabSalary Detail` ssd
        INNER JOIN `tabSalary Slip` ss ON ss.name = ssd.parent
        LEFT JOIN `tabEmployee` e ON e.name = ss.employee
        WHERE ss.docstatus = 1
          AND ss.start_date >= %(from_date)s
          AND ss.end_date   <= %(to_date)s
          AND ssd.parentfield = 'earnings'
          AND ssd.salary_component IN ('Basic', 'Overtime')
        GROUP BY e.department, ssd.salary_component
    """, {"from_date": from_date, "to_date": to_date}, as_dict=True)

    # Build lookup: {department: {component: amount}}
    component_map = {}
    for row in component_rows:
        component_map.setdefault(row.department, {})[row.salary_component] = row.total_amount

    data = []
    for row in dept_rows:
        dept = row.department
        comp = component_map.get(dept, {})
        data.append({
            "department": dept,
            "employee_count": row.employee_count,
            "total_basic": comp.get("Basic", 0),
            "total_overtime": comp.get("Overtime", 0),
            "total_deductions": row.total_deductions,
            "net_pay": row.net_pay,
        })

    return data
