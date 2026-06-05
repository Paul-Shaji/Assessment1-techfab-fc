# Copyright (c) 2026, Paul Shaji and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document

class OvertimeLog(Document):
    def before_save(self):
        # Dynamically calculate the amount before saving
        self.amount = round(self.overtime_hours * self.hourly_rate, 2)

    def on_submit(self):
        # Create and submit a standard Additional Salary record natively
        additional_salary = frappe.get_doc({
            "doctype": "Additional Salary",
            "employee": self.employee,
            "salary_component": "Overtime",
            "amount": self.amount,
            "payroll_date": self.date,
            "company": self.company,
            "overwrite_salary_structure_amount": 1
        })
        additional_salary.insert(ignore_permissions=True)
        additional_salary.submit()
        
        # Link the generated Additional Salary record back for easy auditing
        self.db_set("additional_salary", additional_salary.name)

    def on_cancel(self):
        # Cancel and clean up the linked Additional Salary record
        if self.additional_salary:
            add_sal = frappe.get_doc("Additional Salary", self.additional_salary)
            if add_sal.docstatus == 1:
                add_sal.cancel()
            elif add_sal.docstatus == 0:
                frappe.delete_doc("Additional Salary", self.additional_salary)
            self.db_set("additional_salary", None)