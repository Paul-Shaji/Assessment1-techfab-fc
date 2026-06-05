import frappe
from datetime import datetime, timedelta
from frappe.utils import get_datetime, time_diff_in_hours, getdate, add_days, today
from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday

# =========================================================
# 1. HELPER: Get Logs (PURE SQL)
# =========================================================
def get_all_logs_without_shift(employee, attendance_date):
    start = get_datetime(datetime.combine(attendance_date, datetime.min.time()))
    end = get_datetime(datetime.combine(attendance_date, datetime.max.time()))

    logs = frappe.db.sql("""
        SELECT name, time, log_type, shift
        FROM `tabEmployee Checkin`
        WHERE employee = %s 
        AND time BETWEEN %s AND %s
        AND docstatus = 0
        ORDER BY time ASC
    """, (employee, start, end), as_dict=True)
    return logs

# =========================================================
# 2. CALCULATION LOGIC (Present/Late/Early)
# =========================================================
def force_auto_attendance(*args, **kwargs):
    employee = kwargs.get("employee")
    attendance_date = getdate(kwargs.get("attendance_date"))
    attendance_doc = kwargs.get("attendance_doc")

    if not attendance_doc:
        return

    # A. Gather Logs
    logs = get_all_logs_without_shift(employee, attendance_date)

    # B. Determine Shift
    shift_name = None
    assignments = frappe.db.sql("""
        SELECT shift_type, end_date 
        FROM `tabShift Assignment`
        WHERE employee = %s AND docstatus < 2 AND start_date <= %s
        ORDER BY start_date DESC
    """, (employee, attendance_date), as_dict=True)

    for asm in assignments:
        if not asm.end_date or getdate(asm.end_date) >= attendance_date:
            shift_name = asm.shift_type
            break
    
    if not shift_name and logs:
        for log in logs:
            if log.shift:
                shift_name = log.shift
                break

    # C. Calculate Times
    status = "Absent"
    in_time = None
    out_time = None
    working_hours = 0.0
    late_entry = 0
    early_exit = 0
    early_entry = 0
    late_exit = 0
    should_submit = False

    if logs and len(logs) > 0:
        status = "Present"
        in_time = logs[0]["time"]
        last_log_time = logs[-1]["time"]

        # Checkbox Logic
        if shift_name and in_time:
            try:
                shift = frappe.get_doc("Shift Type", shift_name)
                if shift.start_time and shift.end_time:
                    shift_start_dt = get_datetime(f"{attendance_date} {shift.start_time}")
                    shift_end_dt = get_datetime(f"{attendance_date} {shift.end_time}")
                    if shift_end_dt <= shift_start_dt:
                        shift_end_dt += timedelta(days=1)

                    late_grace = shift.late_entry_grace_period or 0
                    early_grace = shift.early_exit_grace_period or 0

                    if in_time > (shift_start_dt + timedelta(minutes=late_grace)):
                        late_entry = 1 
                    if in_time < (shift_start_dt - timedelta(minutes=late_grace)):
                        early_entry = 1 
                    
                    if (len(logs) > 1) and (last_log_time > in_time):
                        if last_log_time < (shift_end_dt - timedelta(minutes=early_grace)):
                            early_exit = 1 
                        if last_log_time > (shift_end_dt + timedelta(minutes=early_grace)):
                            late_exit = 1
            except Exception:
                pass

        # Duration Logic
        has_checked_out = (len(logs) > 1) and (last_log_time > in_time)
        if has_checked_out:
            out_time = last_log_time
            should_submit = True
            total_work_secs = (out_time - in_time).total_seconds()
            working_hours = round(total_work_secs / 3600, 2)
        else:
            out_time = None
            working_hours = 0.0
            should_submit = False
    else:
        status = "Absent"
        should_submit = True

    # D. Update & Save
    target_doc = attendance_doc
    if attendance_doc.docstatus == 1:
        try:
            attendance_doc.cancel()
            target_doc = frappe.new_doc("Attendance")
            target_doc.employee = employee
            target_doc.attendance_date = attendance_date
            target_doc.company = attendance_doc.company or frappe.db.get_value("Employee", employee, "company")
        except Exception:
            return

    target_doc.status = status
    target_doc.shift = shift_name 
    target_doc.in_time = in_time
    target_doc.out_time = out_time
    target_doc.working_hours = working_hours
    target_doc.overtime_hours = 0.0 
    target_doc.late_entry = late_entry
    target_doc.early_exit = early_exit
    target_doc.early_entry = early_entry
    target_doc.late_exit = late_exit
    
    try:
        if target_doc.is_new():
            target_doc.insert(ignore_permissions=True)
        else:
            target_doc.save(ignore_permissions=True, ignore_version=True)

        if should_submit and target_doc.docstatus == 0:
            target_doc.submit()
            
    except Exception as e:
        frappe.log_error(f"Error saving attendance: {e}", "Auto Attendance Error")


# =========================================================
# 3. ABSENT MARKING LOGIC (Strictly Assigned Employees)
# =========================================================
def mark_absents(start_date, end_date, shift_type_name):
    """
    Iterates from start_date to end_date.
    Finds employees ASSIGNED to this shift.
    If no Attendance and no Logs -> Marks Absent.
    """
    
    delta = timedelta(days=1)
    current_date = getdate(start_date)
    last_date = getdate(end_date)

    while current_date <= last_date:
        
        # A. Get Employees Assigned to this specific Shift on this specific Date
        # We check for Active assignments that overlap with current_date
        assigned_employees = frappe.db.sql("""
            SELECT employee
            FROM `tabShift Assignment`
            WHERE shift_type = %s
            AND docstatus = 1 
            AND status = 'Active'
            AND start_date <= %s
            AND (end_date >= %s OR end_date IS NULL)
        """, (shift_type_name, current_date, current_date), as_dict=True)

        for asm in assigned_employees:
            emp_id = asm.employee

            # B. Check if Attendance already exists (Present, Leave, or Absent)
            if frappe.db.exists("Attendance", {"employee": emp_id, "attendance_date": current_date, "docstatus": ["<", 2]}):
                continue 

            # C. Check if Employee has ANY logs (Don't mark absent if logs exist but not processed)
            start_time = get_datetime(datetime.combine(current_date, datetime.min.time()))
            end_time = get_datetime(datetime.combine(current_date, datetime.max.time()))
            
            has_logs = frappe.db.count("Employee Checkin", {
                "employee": emp_id,
                "time": ["between", [start_time, end_time]],
                "docstatus": 0
            })

            if has_logs > 0:
                continue 

            # D. Check if Holiday
            # Need to fetch company/holiday list for this specific employee
            emp_details = frappe.db.get_value("Employee", emp_id, ["company", "holiday_list"], as_dict=True)
            if not emp_details: continue

            holiday_list = emp_details.holiday_list or frappe.db.get_value("Company", emp_details.company, "default_holiday_list")
            if holiday_list and is_holiday(holiday_list, current_date):
                continue 

            # E. Mark ABSENT
            try:
                doc = frappe.new_doc("Attendance")
                doc.employee = emp_id
                doc.attendance_date = current_date
                doc.status = "Absent"
                doc.company = emp_details.company
                doc.shift = shift_type_name
                doc.insert(ignore_permissions=True)
                doc.submit()
                frappe.log_error(f"Marked Absent: {emp_id} on {current_date}", "Auto Attendance Absent")
            except Exception as e:
                frappe.log_error(f"Failed to mark absent for {emp_id}: {e}", "Auto Attendance Error")

        current_date += delta


# =========================================================
# 4. BULK PROCESSOR (Triggered by Button)
# =========================================================
@frappe.whitelist()
def process_bulk_attendance_override(shift_type_name=None, **kwargs):
    """
    Called when 'Mark Attendance' button is clicked.
    """
    
    # 1. Determine Start Date based on Shift Type Settings
    start_date = add_days(today(), -4) # Default
    
    if shift_type_name:
        process_after = frappe.db.get_value("Shift Type", shift_type_name, "process_attendance_after")
        if process_after:
            safe_date = add_days(today(), -30)
            if getdate(process_after) > getdate(safe_date):
                start_date = process_after
            else:
                start_date = safe_date

    # 2. Process PRESENTS (Logs)
    # We process logs regardless of shift assignment to ensure late checkouts are caught
    recent_logs = frappe.db.sql("""
        SELECT DISTINCT employee, DATE(time) as log_date
        FROM `tabEmployee Checkin`
        WHERE time >= %s
    """, (start_date,), as_dict=True)

    present_count = 0
    for item in recent_logs:
        employee = item.employee
        att_date = getdate(item.log_date)

        attendance_name = frappe.db.get_value("Attendance", {
            "employee": employee,
            "attendance_date": att_date
        })

        attendance_doc = None
        if attendance_name:
            attendance_doc = frappe.get_doc("Attendance", attendance_name)
        else:
            try:
                attendance_doc = frappe.new_doc("Attendance")
                attendance_doc.employee = employee
                attendance_doc.attendance_date = att_date
                attendance_doc.status = "Present"
                attendance_doc.company = frappe.db.get_value("Employee", employee, "company")
                attendance_doc.insert(ignore_permissions=True)
                frappe.db.commit() 
            except Exception:
                continue

        if attendance_doc:
            force_auto_attendance(
                employee=employee,
                attendance_date=att_date,
                attendance_doc=attendance_doc
            )
            present_count += 1
    
    # 3. Process ABSENTS (Missing Logs)
    # Only runs if we have a specific Shift Type Name (passed from the button)
    if shift_type_name:
        mark_absents(start_date, today(), shift_type_name)

    frappe.msgprint(f"Processed Attendance. Checked from {start_date}.")

def get_employee_shift_hours(employee):
    return 9
  