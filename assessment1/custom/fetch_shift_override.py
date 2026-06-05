import frappe
from frappe.utils import get_datetime
from datetime import timedelta

try:
    from hrms.hr.doctype.employee_checkin.employee_checkin import EmployeeCheckin
    from hrms.hr.doctype.shift_assignment.shift_assignment import get_actual_start_end_datetime_of_shift
except ImportError:
    from erpnext.hr.doctype.employee_checkin.employee_checkin import EmployeeCheckin
    from erpnext.hr.doctype.shift_assignment.shift_assignment import get_actual_start_end_datetime_of_shift

def allow_offshift_fetch_shift(self):
    """
    Forces check-in to be valid by removing Skip/Offshift flags.
    """
    checkin_datetime = get_datetime(self.time)
    
    shift_data = get_actual_start_end_datetime_of_shift(
        self.employee, checkin_datetime, True
    )

    # FORCE VALIDITY FOR ALL LOGS
    self.skip_auto_attendance = 0  # <--- CRITICAL FORCE UNCHECK
    self.offshift = 0              # <--- CRITICAL FORCE VALID

    if not shift_data:
        self.shift = None
        self.shift_actual_start = None
        self.shift_actual_end = None
        self.shift_start = None
        self.shift_end = None
        return

    self.shift = shift_data.shift_type.name
    self.shift_actual_start = shift_data.actual_start
    self.shift_actual_end = shift_data.actual_end
    self.shift_start = shift_data.start_datetime
    self.shift_end = shift_data.end_datetime

    # Removed the "Strictly based on Log Type" error to allow flow
    pass

def apply_patch():
    EmployeeCheckin.fetch_shift = allow_offshift_fetch_shift