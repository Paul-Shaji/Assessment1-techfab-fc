import frappe
from hrms.hr.doctype.shift_type.shift_type import ShiftType
from assessment1.custom.auto_attendance_override import process_bulk_attendance_override

@frappe.whitelist()
def custom_process_auto_attendance(self):
    """
    Replaces ShiftType.process_auto_attendance.
    Passes the Shift Name to the bulk processor.
    """
    # We pass self.name so the processor can look up 'Process Attendance After'
    process_bulk_attendance_override(shift_type_name=self.name)

def apply_shift_patch():
    ShiftType.process_auto_attendance = custom_process_auto_attendance