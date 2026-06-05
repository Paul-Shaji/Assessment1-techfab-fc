import frappe
from hrms.hr.doctype.employee_checkin.employee_checkin import mark_attendance_and_link_log
# We will directly import and call force_auto_attendance from your other override
from assessment1.custom.auto_attendance_override import force_auto_attendance
from frappe.utils import get_datetime
from datetime import date # Import date for clarity

def override_auto_attendance(doc, method):
    """
    After every checkin → try marking/updating attendance.
    This ensures OUT logs (even outside shift) are included and attendance
    is always updated with the first IN and last OUT.
    """
    if doc.skip_auto_attendance:
        return

    employee = doc.employee
    attendance_date = doc.time.date() # This is a datetime.date object

    # Check if an attendance record already exists for the day using frappe.db.exists
    attendance_name = frappe.db.get_value("Attendance", {
        "employee": employee,
        "attendance_date": attendance_date
    })

    attendance_doc = None
    if attendance_name:
        # If it exists, fetch it
        attendance_doc = frappe.get_doc("Attendance", attendance_name)
    else:
        # If no attendance record exists, create one first.
        try:
            attendance_doc = frappe.new_doc("Attendance")
            attendance_doc.employee = employee
            attendance_doc.attendance_date = attendance_date
            attendance_doc.status = "Present" # Default status, will be refined by force_auto_attendance
            attendance_doc.insert(ignore_permissions=True, ignore_mandatory=True)
            frappe.db.commit() # Ensure the new doc is committed before proceeding
        except Exception as e:
            frappe.log_error(f"Error creating new Attendance for {employee} on {attendance_date}: {e}", "GRC Attendance Create Error")
            frappe.throw(f"Failed to create new Attendance record: {e}")
            return # Stop execution if creation fails

    if not attendance_doc:
        frappe.throw("Attendance document could not be created or retrieved.")
        return

    # Now, call your custom force_auto_attendance with the attendance_doc
    # It will fetch logs and update the attendance_doc's fields.
    try:
        force_auto_attendance(
            employee=employee,
            attendance_date=attendance_date,
            attendance_doc=attendance_doc # Pass the document to be updated
        )
        # force_auto_attendance already calls attendance.save()
    except Exception as e:
        frappe.log_error(f"Auto Attendance Override Error for {employee} on {attendance_date}: {e}", "GRC Auto Attendance")
        # Depending on desired behavior, you might want to re-raise or just log
        frappe.throw(f"Failed to calculate and update attendance: {e}")