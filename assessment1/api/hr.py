# import frappe


# def overtime_hourly_rate(basic: float, days: int = 26, hours: int = 8) -> float:
#     return basic / days / hours


# def calculate_overtime_on_salary_slip(doc, method=None):
#     """
#     Runs before_save on Salary Slip.
#     For Production department employees:
#       - Sums overtime_hours from submitted Attendance records in the pay period
#       - Sets the Overtime earning component amount
#     For all employees:
#       - Calculates attendance deduction for absent days
#     """
#     if not doc.employee:
#         return

#     department = frappe.db.get_value("Employee", doc.employee, "department")

#     # --- Overtime (Production only) ---
#     if department == "Production":
#         total_overtime_hours = frappe.db.sql("""
#             SELECT COALESCE(SUM(custom_overtime_hours), 0)
#             FROM `tabAttendance`
#             WHERE
#                 employee = %s
#                 AND attendance_date BETWEEN %s AND %s
#                 AND docstatus = 1
#                 AND status = 'Present'
#         """, (doc.employee, doc.start_date, doc.end_date))[0][0] or 0

#         basic_amount = get_component_amount(doc, "Basic")
#         hourly_rate = overtime_hourly_rate(basic_amount)
#         overtime_amount = round(total_overtime_hours * hourly_rate, 2)

#         set_component_amount(doc, "Overtime", overtime_amount)
#     else:
#         # Zero out overtime for non-Production employees
#         set_component_amount(doc, "Overtime", 0)

#     # --- Attendance Deduction (all employees) ---
#     absent_days = frappe.db.sql("""
#         SELECT COUNT(*)
#         FROM `tabAttendance`
#         WHERE
#             employee = %s
#             AND attendance_date BETWEEN %s AND %s
#             AND docstatus = 1
#             AND status = 'Absent'
#     """, (doc.employee, doc.start_date, doc.end_date))[0][0] or 0

#     if absent_days > 0:
#         basic_amount = get_component_amount(doc, "Basic")
#         daily_rate = basic_amount / 26
#         deduction_amount = round(absent_days * daily_rate, 2)
#         set_component_amount(doc, "Attendance Deduction", deduction_amount)
#     else:
#         set_component_amount(doc, "Attendance Deduction", 0)


# def get_component_amount(doc, component_name):
#     """Get amount of a salary component from the slip."""
#     for row in doc.earnings:
#         if row.salary_component == component_name:
#             return row.amount or 0
#     for row in doc.deductions:
#         if row.salary_component == component_name:
#             return row.amount or 0
#     return 0


# def set_component_amount(doc, component_name, amount):
#     """Set amount of a salary component in the slip if it exists."""
#     for row in doc.earnings:
#         if row.salary_component == component_name:
#             row.amount = amount
#             return
#     for row in doc.deductions:
#         if row.salary_component == component_name:
#             row.amount = amount
#             return


import frappe

# =========================================================================
# 1. GENERAL HELPERS
# =========================================================================

def get_basic_salary_amount(employee, company):
    assignment = frappe.db.get_value(
        "Salary Structure Assignment",
        {"employee": employee, "docstatus": 1, "company": company},
        ["salary_structure", "base"],
        as_dict=True
    )
    if not assignment:
        return 0.0
    if assignment.base:
        return assignment.base
    
    basic_amount = frappe.db.get_value(
        "Salary Detail",
        {"parent": assignment.salary_structure, "salary_component": "Basic", "parenttype": "Salary Structure"},
        "amount"
    )
    return basic_amount or 0.0


# =========================================================================
# 2. ATTENDANCE BEFORE_SAVE: Calculate custom_overtime_hours
# =========================================================================

def _get_shift_standard_hours(shift_name, default=8.0):
    if not shift_name:
        return default
    shift = frappe.db.get_value(
        "Shift Type", shift_name, ["start_time", "end_time"], as_dict=True
    )
    if not shift or shift.start_time is None or shift.end_time is None:
        return default
    duration = (shift.end_time - shift.start_time).total_seconds()
    return duration / 3600 if duration > 0 else default


def calculate_attendance_overtime(doc, method=None):
    """
    Runs before_save on Attendance.
    For Production department employees:
        custom_overtime_hours = working_hours - standard shift hours
    All others are zeroed out.
    """
    if doc.status != "Present" or not doc.working_hours:
        doc.custom_overtime_hours = 0
        return

    department = frappe.db.get_value("Employee", doc.employee, "department")
    if not department or "Production" not in department:
        doc.custom_overtime_hours = 0
        return

    standard_hours = _get_shift_standard_hours(doc.shift)
    doc.custom_overtime_hours = round(max(0.0, doc.working_hours - standard_hours), 2)


# =========================================================================
# 3. NEW OVERTIME FLOW: Triggered when Attendance is Submitted
# =========================================================================

def create_overtime_log_from_attendance(doc, method=None):
    if not doc.custom_overtime_hours or doc.custom_overtime_hours <= 0:
        return

    exists = frappe.db.exists("Overtime Log", {
        "employee": doc.employee,
        "date": doc.attendance_date,
        "docstatus": ["<", 2]
    })
    if exists:
        return

    basic_salary = get_basic_salary_amount(doc.employee, doc.company)
    hourly_rate = basic_salary / 26 / 8
    amount = round(doc.custom_overtime_hours * hourly_rate, 2)

    overtime_log = frappe.get_doc({
        "doctype": "Overtime Log",
        "employee": doc.employee,
        "employee_name": doc.employee_name,
        "date": doc.attendance_date,
        "overtime_hours": doc.custom_overtime_hours,
        "hourly_rate": hourly_rate,
        "amount": amount,
        "company": doc.company,
        "attendance": doc.name
    })
    overtime_log.insert(ignore_permissions=True)
    overtime_log.submit()


# =========================================================================
# 3. SALARY SLIP HOOK: Only processes Attendance Deductions
# =========================================================================

def calculate_overtime_on_salary_slip(doc, method=None):
    if not doc.employee:
        return

    absent_days = frappe.db.sql("""
        SELECT COUNT(*)
        FROM `tabAttendance`
        WHERE
            employee = %s
            AND attendance_date BETWEEN %s AND %s
            AND docstatus = 1
            AND status = 'Absent'
    """, (doc.employee, doc.start_date, doc.end_date))[0][0] or 0

    if absent_days > 0:
        basic_amount = get_basic_salary_amount(doc.employee, doc.company)
        daily_rate = basic_amount / 26
        deduction_amount = round(absent_days * daily_rate, 2)
        set_component_amount(doc, "Attendance Deduction", deduction_amount)
    else:
        set_component_amount(doc, "Attendance Deduction", 0)


def set_component_amount(doc, component_name, amount):
    for row in doc.deductions:
        if row.salary_component == component_name:
            row.amount = amount
            return
            
    if amount > 0:
        doc.append("deductions", {
            "salary_component": component_name,
            "amount": amount,
            "default_amount": amount
        })