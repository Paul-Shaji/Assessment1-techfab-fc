import frappe
from frappe import _
from frappe.auth import LoginManager
from frappe.utils import nowdate, add_days, getdate, get_first_day, get_last_day, flt, cint


# ─────────────────────────────────────────────────────────────────────────────
#  Role → module routing
# ─────────────────────────────────────────────────────────────────────────────

# Maps a Frappe role to a dashboard module key used by the sidebar/router.
ROLE_MODULE_MAP = {
    "Sales Manager": "sales",
    "Sales User": "sales",
    "Purchase Manager": "purchase",
    "Purchase User": "purchase",
    "Stock Manager": "purchase",
    "Manufacturing Manager": "manufacturing",
    "Manufacturing User": "manufacturing",
    "Maintenance Manager": "assets",
    "Maintenance User": "assets",
    "Service User": "assets",
    "HR Manager": "hr",
    "HR User": "hr",
}

# Route each module key resolves to in the SPA.
MODULE_ROUTE = {
    "sales": "/sales",
    "purchase": "/purchase",
    "manufacturing": "/manufacturing",
    "assets": "/assets",
    "hr": "/hr",
}

# Reward tiers — mirrors assessment1.api.rewards.calculate_reward_points.
REWARD_TIERS = [
    {"label": "Below ₹50,000", "rule": "1 point per ₹10,000"},
    {"label": "₹50,000 – ₹1,00,000", "rule": "8 points (flat)"},
    {"label": "Above ₹1,00,000", "rule": "15 points (flat)"},
]


def _allowed_modules(roles):
    """Distinct dashboard modules a set of roles can see."""
    if "System Manager" in roles:
        return ["sales", "purchase", "manufacturing", "assets", "hr"]
    seen = []
    for r in roles:
        m = ROLE_MODULE_MAP.get(r)
        if m and m not in seen:
            seen.append(m)
    return seen


def _resolve_home_route(roles):
    """Default landing route after login based on the user's roles."""
    if "System Manager" in roles:
        return "/dashboard"
    modules = _allowed_modules(roles)
    if modules:
        return MODULE_ROUTE[modules[0]]
    return "/dashboard"


def _require_any_role(allowed):
    """Server-side guard for a fetcher. System Manager always passes."""
    user_roles = set(frappe.get_roles())
    if "System Manager" in user_roles:
        return
    if not user_roles.intersection(allowed):
        frappe.throw(
            _("You do not have permission to view this dashboard."),
            frappe.PermissionError,
        )


# ─────────────────────────────────────────────────────────────────────────────
#  Authentication
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    """
    Wrapper around Frappe's LoginManager. Authenticates, establishes the
    httpOnly session cookie, and returns the user's profile + roles in one
    round-trip so the SPA can route immediately. Bad credentials raise
    frappe.AuthenticationError (generic — no user enumeration).
    """
    login_manager = LoginManager()
    login_manager.authenticate(user=usr, pwd=pwd)
    login_manager.post_login()

    user = frappe.session.user
    roles = frappe.get_roles(user)
    return {
        "success": True,
        "user": user,
        "full_name": frappe.db.get_value("User", user, "full_name"),
        "roles": roles,
        "modules": _allowed_modules(roles),
        "home_route": _resolve_home_route(roles),
    }


@frappe.whitelist()
def get_current_user_roles():
    """
    Active user's identity, roles and visible modules. The SPA's AuthContext
    calls this on load to revalidate the session — it is the source of truth,
    not any cached client state.
    """
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Not logged in."), frappe.AuthenticationError)

    roles = frappe.get_roles(user)
    return {
        "user": user,
        "email": user,
        "full_name": frappe.db.get_value("User", user, "full_name"),
        "roles": roles,
        "modules": _allowed_modules(roles),
        "home_route": _resolve_home_route(roles),
    }


@frappe.whitelist()
def logout():
    """Invalidate the current session server-side."""
    frappe.local.login_manager.logout()
    frappe.db.commit()
    return {"success": True}


# ─────────────────────────────────────────────────────────────────────────────
#  Executive dashboard — the 6 metric cards
# ─────────────────────────────────────────────────────────────────────────────

def _count_with_trend(doctype, filters=None, date_field="creation"):
    """
    Returns {value, trend, trend_label} where `trend` is the % of the current
    total that was added since yesterday — i.e. (created_today / prior_total).
    """
    filters = filters or {}
    total = frappe.db.count(doctype, filters)

    today = getdate(nowdate())
    prior_filters = dict(filters)
    prior_filters[date_field] = ["<", str(today)]
    prior_total = frappe.db.count(doctype, prior_filters)

    created_today = total - prior_total
    if prior_total > 0:
        trend = round((created_today / prior_total) * 100, 1)
    elif created_today > 0:
        trend = 100.0
    else:
        trend = 0.0

    return {"value": total, "trend": trend, "trend_label": "since yesterday"}


def _total_reward_points():
    return cint(
        frappe.db.sql(
            "SELECT COALESCE(SUM(points_earned), 0) FROM `tabSalesperson Reward Log`"
        )[0][0]
    )


@frappe.whitelist()
def get_dashboard_stats():
    """The 6 executive metric cards with trend badges."""
    sales_orders = _count_with_trend("Sales Order", {"docstatus": 1})

    # "Pending Purchases" mirrors the TechFab Management Report metric:
    # submitted Material Requests awaiting fulfilment.
    pending_purchases = _count_with_trend("Material Request", {"docstatus": 1})

    production_in_progress = _count_with_trend(
        "Work Order", {"docstatus": 1, "status": "In Process"}
    )
    production_completed = _count_with_trend(
        "Work Order", {"docstatus": 1, "status": "Completed"}
    )

    total_employees = {
        "value": frappe.db.count("Employee", {"status": "Active"}),
        "trend": 0.0,
        "trend_label": "",
    }
    reward_points = {"value": _total_reward_points(), "trend": 0.0, "trend_label": ""}

    return {
        "cards": [
            {"key": "sales_orders", "label": "Sales Orders", "icon": "shopping-cart", **sales_orders},
            {"key": "pending_purchases", "label": "Pending Purchases", "icon": "package", **pending_purchases},
            {"key": "production_in_progress", "label": "Production In Progress", "icon": "loader", **production_in_progress},
            {"key": "production_completed", "label": "Production Completed", "icon": "check-circle", **production_completed},
            {"key": "total_employees", "label": "Total Employees", "icon": "users", **total_employees},
            {"key": "reward_points", "label": "Total Reward Points", "icon": "award", **reward_points},
        ]
    }


@frappe.whitelist()
def get_notifications():
    """Header notifications — assets due for maintenance within 90 days."""
    today = getdate(nowdate())
    window = add_days(today, 90)
    due = frappe.db.sql(
        """
        SELECT am.asset_name, amt.maintenance_task, amt.next_due_date
        FROM `tabAsset Maintenance Task` amt
        INNER JOIN `tabAsset Maintenance` am ON am.name = amt.parent
        WHERE amt.next_due_date BETWEEN %s AND %s
        ORDER BY amt.next_due_date ASC
        """,
        (today, window),
        as_dict=True,
    )
    for d in due:
        d["days_to_due"] = (getdate(d.next_due_date) - today).days
    return {"count": len(due), "items": due}


# ─────────────────────────────────────────────────────────────────────────────
#  Sales
# ─────────────────────────────────────────────────────────────────────────────

_CATEGORY_BY_PREFIX = {"GOV": "Government", "COR": "Corporate", "RET": "Retail"}


@frappe.whitelist()
def get_sales_dashboard():
    _require_any_role(["Sales Manager", "Sales User"])

    quotations = frappe.get_all(
        "Quotation",
        filters={"docstatus": ["<", 2]},
        fields=["name", "party_name", "customer_name", "grand_total", "status", "transaction_date"],
        order_by="creation desc",
        limit=50,
    )

    orders = frappe.get_all(
        "Sales Order",
        filters={"docstatus": ["<", 2]},
        fields=["name", "customer", "customer_name", "grand_total", "status", "transaction_date"],
        order_by="creation desc",
        limit=200,
    )

    buckets = {
        cat: {"category": cat, "prefix": pfx, "count": 0, "total": 0.0, "orders": []}
        for pfx, cat in _CATEGORY_BY_PREFIX.items()
    }
    buckets["Other"] = {"category": "Other", "prefix": "", "count": 0, "total": 0.0, "orders": []}

    for o in orders:
        prefix = (o.name.split("-")[0] or "").upper()
        cat = _CATEGORY_BY_PREFIX.get(prefix, "Other")
        b = buckets[cat]
        b["count"] += 1
        b["total"] += flt(o.grand_total)
        if len(b["orders"]) < 25:
            b["orders"].append(o)

    reward_ledger = frappe.get_all(
        "Salesperson Reward Log",
        fields=["sales_person", "customer", "collection_amount", "points_earned", "date", "remarks"],
        order_by="date desc, creation desc",
        limit=100,
    )

    reward_summary = frappe.db.sql(
        """
        SELECT sales_person,
               SUM(points_earned)     AS total_points,
               SUM(collection_amount) AS total_collection,
               COUNT(*)               AS entries
        FROM `tabSalesperson Reward Log`
        GROUP BY sales_person
        ORDER BY total_points DESC
        """,
        as_dict=True,
    )

    return {
        "quotations": quotations,
        "orders_by_category": [buckets[c] for c in ("Government", "Corporate", "Retail", "Other")],
        "reward_ledger": reward_ledger,
        "reward_summary": reward_summary,
        "reward_tiers": REWARD_TIERS,
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Purchase / Inventory
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_purchase_dashboard():
    _require_any_role(["Purchase Manager", "Purchase User", "Stock Manager"])

    rows = frappe.db.sql(
        """
        SELECT b.item_code,
               i.item_name,
               i.item_group,
               i.stock_uom,
               SUM(b.actual_qty)    AS actual_qty,
               SUM(b.reserved_qty)  AS reserved_qty,
               SUM(b.ordered_qty)   AS ordered_qty,
               SUM(b.projected_qty) AS projected_qty
        FROM `tabBin` b
        INNER JOIN `tabItem` i ON i.name = b.item_code
        WHERE i.disabled = 0 AND i.is_stock_item = 1
        GROUP BY b.item_code
        ORDER BY (SUM(b.actual_qty) - SUM(b.reserved_qty)) ASC
        """,
        as_dict=True,
    )

    inventory = []
    for r in rows:
        available = flt(r.actual_qty) - flt(r.reserved_qty)
        shortage = max(flt(r.reserved_qty) - flt(r.actual_qty), 0.0)
        inventory.append({
            "item_code": r.item_code,
            "item_name": r.item_name,
            "item_group": r.item_group,
            "uom": r.stock_uom,
            "available": available,           # in stock and unreserved
            "shortage": shortage,             # demand beyond stock (to be purchased)
            "ordered": flt(r.ordered_qty),    # already on a Purchase Order
            "projected": flt(r.projected_qty),
        })

    active_purchase_orders = frappe.get_all(
        "Purchase Order",
        filters={"docstatus": 1, "status": ["in", ["To Receive and Bill", "To Receive", "To Bill"]]},
        fields=["name", "supplier", "supplier_name", "grand_total", "status", "transaction_date", "per_received"],
        order_by="transaction_date desc",
        limit=100,
    )

    return {"inventory": inventory, "active_purchase_orders": active_purchase_orders}


# ─────────────────────────────────────────────────────────────────────────────
#  Manufacturing
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_manufacturing_dashboard():
    _require_any_role(["Manufacturing Manager", "Manufacturing User"])

    work_orders = frappe.get_all(
        "Work Order",
        filters={"docstatus": ["<", 2]},
        fields=["name", "production_item", "item_name", "qty", "produced_qty", "status", "planned_start_date"],
        order_by="creation desc",
        limit=200,
    )

    by_item = {}
    totals = {"planned": 0.0, "under_production": 0.0, "completed": 0.0}
    for w in work_orders:
        a = by_item.setdefault(
            w.production_item,
            {"item_code": w.production_item, "item_name": w.item_name,
             "planned": 0.0, "under_production": 0.0, "completed": 0.0},
        )
        if w.status == "Completed":
            a["completed"] += flt(w.produced_qty)
            totals["completed"] += flt(w.produced_qty)
        elif w.status in ("In Process", "Stopped"):
            remaining = flt(w.qty) - flt(w.produced_qty)
            a["under_production"] += remaining
            a["completed"] += flt(w.produced_qty)
            totals["under_production"] += remaining
            totals["completed"] += flt(w.produced_qty)
        else:  # Draft / Not Started
            a["planned"] += flt(w.qty)
            totals["planned"] += flt(w.qty)

    try:
        production_plans = frappe.get_all(
            "Production Plan",
            filters={"docstatus": ["<", 2]},
            fields=["name", "status", "posting_date", "total_planned_qty", "total_produced_qty"],
            order_by="creation desc",
            limit=50,
        )
    except Exception:
        production_plans = []

    return {
        "work_orders": work_orders,
        "by_item": list(by_item.values()),
        "totals": totals,
        "production_plans": production_plans,
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Assets / Service
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_asset_dashboard():
    _require_any_role(["Maintenance Manager", "Maintenance User", "Service User"])

    assets = frappe.get_all(
        "Asset",
        filters={"docstatus": 1},
        fields=["name", "asset_name", "asset_category", "location", "status",
                "purchase_date", "gross_purchase_amount"],
        order_by="asset_category asc, asset_name asc",
        limit=200,
    )

    today = getdate(nowdate())
    window = add_days(today, 90)
    tasks = frappe.db.sql(
        """
        SELECT am.asset_name,
               amt.maintenance_task,
               amt.maintenance_type,
               amt.next_due_date,
               amt.last_completion_date
        FROM `tabAsset Maintenance Task` amt
        INNER JOIN `tabAsset Maintenance` am ON am.name = amt.parent
        WHERE amt.next_due_date <= %s
        ORDER BY amt.next_due_date ASC
        """,
        (window,),
        as_dict=True,
    )

    for t in tasks:
        days = (getdate(t.next_due_date) - today).days
        t["days_to_due"] = days
        if days < 0:
            t["severity"] = "overdue"
        elif days <= 30:
            t["severity"] = "critical"
        else:
            t["severity"] = "warning"

    return {"assets": assets, "maintenance_alerts": tasks}


# ─────────────────────────────────────────────────────────────────────────────
#  HR & Payroll
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_hr_dashboard(attendance_date=None):
    _require_any_role(["HR Manager", "HR User"])

    day = attendance_date or nowdate()
    first_day = get_first_day(getdate(nowdate()))
    last_day = get_last_day(getdate(nowdate()))

    attendance = frappe.get_all(
        "Attendance",
        filters={"attendance_date": day, "docstatus": 1},
        fields=["employee", "employee_name", "department", "status",
                "custom_overtime_hours", "in_time", "out_time"],
        order_by="employee_name asc",
    )

    overtime_logs = frappe.db.sql(
        """
        SELECT a.employee, a.employee_name, a.attendance_date,
               a.custom_overtime_hours, e.department
        FROM `tabAttendance` a
        LEFT JOIN `tabEmployee` e ON e.name = a.employee
        WHERE a.docstatus = 1
          AND a.custom_overtime_hours > 0
          AND e.department = %s
          AND a.attendance_date BETWEEN %s AND %s
        ORDER BY a.attendance_date DESC
        """,
        ("Production", first_day, last_day),
        as_dict=True,
    )

    payroll = frappe.db.sql(
        """
        SELECT ss.name AS salary_slip,
               ss.employee, ss.employee_name, e.department, ss.net_pay,
               MAX(CASE WHEN sd.salary_component = 'Basic'
                        AND sd.parentfield = 'earnings'   THEN sd.amount END) AS basic,
               MAX(CASE WHEN sd.salary_component = 'Overtime'
                        AND sd.parentfield = 'earnings'   THEN sd.amount END) AS overtime,
               MAX(CASE WHEN sd.salary_component = 'Attendance Deduction'
                        AND sd.parentfield = 'deductions' THEN sd.amount END) AS attendance_deduction
        FROM `tabSalary Slip` ss
        LEFT JOIN `tabEmployee` e ON e.name = ss.employee
        LEFT JOIN `tabSalary Detail` sd ON sd.parent = ss.name
        WHERE ss.docstatus = 1
          AND ss.start_date >= %s
          AND ss.end_date   <= %s
        GROUP BY ss.name
        ORDER BY e.department, ss.employee_name
        """,
        (first_day, last_day),
        as_dict=True,
    )

    return {
        "attendance": attendance,
        "overtime_logs": overtime_logs,
        "payroll": payroll,
        "period": {"from_date": str(first_day), "to_date": str(last_day)},
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Reports (reuse the existing Script Report logic)
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_techfab_management_report():
    from assessment1.assessment1.report.techfab_management_report.techfab_management_report import execute
    columns, data = execute({})
    return {"columns": columns, "data": data}


@frappe.whitelist()
def get_payroll_summary_report(from_date=None, to_date=None):
    from assessment1.assessment1.report.department_wise_payroll_summary.department_wise_payroll_summary import execute
    if not from_date:
        from_date = str(get_first_day(getdate(nowdate())))
    if not to_date:
        to_date = str(get_last_day(getdate(nowdate())))
    columns, data = execute({"from_date": from_date, "to_date": to_date})
    return {"columns": columns, "data": data, "from_date": from_date, "to_date": to_date}
