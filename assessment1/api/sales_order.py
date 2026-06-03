import frappe
from frappe.model.naming import make_autoname


CUSTOMER_TYPE_PREFIX = {
    "Government": "GOV-.####",
    "Corporate":  "COR-.####",
    "Retail":     "RET-.####",
}


def set_naming_series(doc, method=None):
    """
    Runs before_insert on Sales Order.
    Reads customer_type from the linked Customer and generates
    the document name directly using make_autoname.
    Independent counters per prefix — GOV, COR, RET are separate sequences.
    """
    if not doc.customer:
        frappe.throw("Customer is required to determine naming series.")

    customer_type = frappe.db.get_value(
        "Customer", doc.customer, "custom_customer_type"
    )

    if not customer_type:
        frappe.throw(
            f"Customer '{doc.customer}' does not have a Customer Type set. "
            "Please set it on the Customer record before creating a Sales Order."
        )

    prefix = CUSTOMER_TYPE_PREFIX.get(customer_type)

    if not prefix:
        frappe.throw(
            f"Unknown customer type '{customer_type}'. "
            "Expected: Government, Corporate, or Retail."
        )
        
    doc.naming_series = prefix