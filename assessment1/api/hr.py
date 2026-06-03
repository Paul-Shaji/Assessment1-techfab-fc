import frappe


OVERTIME_HOURLY_RATE_FORMULA = lambda basic, days=26, hours=8: basic / days / hours


def calculate_overtime_on_salary_slip(doc, method=None):
    """
    Runs before_save on Salary Slip.
    For Production department employees:
      - Sums overtime_hours from submitted Attendance records in the pay period
      - Sets the Overtime earning component amount
    For all employees:
      - Calculates attendance deduction for absent days
    """
    if not doc.employee:
        return

    department = frappe.db.get_value("Employee", doc.employee, "department")

    # --- Overtime (Production only) ---
    if department == "Production":
        total_overtime_hours = frappe.db.sql("""
            SELECT COALESCE(SUM(custom_overtime_hours), 0)
            FROM `tabAttendance`
            WHERE
                employee = %s
                AND attendance_date BETWEEN %s AND %s
                AND docstatus = 1
                AND status = 'Present'
        """, (doc.employee, doc.start_date, doc.end_date))[0][0] or 0

        basic_amount = get_component_amount(doc, "Basic")
        hourly_rate = OVERTIME_HOURLY_RATE_FORMULA(basic_amount)
        overtime_amount = round(total_overtime_hours * hourly_rate, 2)

        set_component_amount(doc, "Overtime", overtime_amount)
    else:
        # Zero out overtime for non-Production employees
        set_component_amount(doc, "Overtime", 0)

    # --- Attendance Deduction (all employees) ---
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
        basic_amount = get_component_amount(doc, "Basic")
        daily_rate = basic_amount / 26
        deduction_amount = round(absent_days * daily_rate, 2)
        set_component_amount(doc, "Attendance Deduction", deduction_amount)
    else:
        set_component_amount(doc, "Attendance Deduction", 0)


def get_component_amount(doc, component_name):
    """Get amount of a salary component from the slip."""
    for row in doc.earnings:
        if row.salary_component == component_name:
            return row.amount or 0
    for row in doc.deductions:
        if row.salary_component == component_name:
            return row.amount or 0
    return 0


def set_component_amount(doc, component_name, amount):
    """Set amount of a salary component in the slip if it exists."""
    for row in doc.earnings:
        if row.salary_component == component_name:
            row.amount = amount
            return
    for row in doc.deductions:
        if row.salary_component == component_name:
            row.amount = amount
            return
