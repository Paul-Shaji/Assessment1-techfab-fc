import frappe
from frappe.utils import nowdate


@frappe.whitelist()
def get_total_reward_points():
    total = frappe.db.sql("""
        SELECT COALESCE(SUM(points_earned), 0)
        FROM `tabSalesperson Reward Log`
    """)[0][0] or 0
    return int(total)

def calculate_reward_points(collection_amount):
    """
    Points rules:
    Below 50,000       → 1 point per 10,000
    50,000 - 1,00,000  → 8 points flat
    Above 1,00,000     → 15 points flat
    """
    if collection_amount <= 0:
        return 0
    if collection_amount < 50000:
        return int(collection_amount // 10000)
    elif collection_amount <= 100000:
        return 8
    else:
        return 15


def create_reward_log_on_payment(doc, method=None):
    """
    Runs on_submit of Payment Entry.
    If payment is against a Sales Invoice that has a Sales Person,
    calculate reward points and create a Salesperson Reward Log.
    """
    if doc.payment_type != "Receive":
        return

    if not doc.references:
        return

    for ref in doc.references:
        if ref.reference_doctype != "Sales Invoice":
            continue

        sales_invoice = frappe.get_doc("Sales Invoice", ref.reference_name)

        if not sales_invoice.sales_team:
            continue

        collection_amount = ref.allocated_amount

        if not collection_amount or collection_amount <= 0:
            continue

        points = calculate_reward_points(collection_amount)

        if points <= 0:
            continue

        for sales_person_row in sales_invoice.sales_team:
            # Check if log already exists for this payment + sales person
            existing = frappe.db.exists("Salesperson Reward Log", {
                "payment_entry": doc.name,
                "sales_person": sales_person_row.sales_person
            })

            if existing:
                continue

            remarks = get_remarks(collection_amount, points)

            frappe.get_doc({
                "doctype": "Salesperson Reward Log",
                "sales_person": sales_person_row.sales_person,
                "payment_entry": doc.name,
                "customer": doc.party,
                "collection_amount": collection_amount,
                "points_earned": points,
                "date": doc.posting_date or nowdate(),
                "remarks": remarks
            }).insert(ignore_permissions=True)

    frappe.db.commit()


def get_remarks(amount, points):
    if amount < 50000:
        return f"₹{amount:,.0f} collected — 1 point per ₹10,000 = {points} points"
    elif amount <= 100000:
        return f"₹{amount:,.0f} collected — flat 8 points (₹50k–₹1L slab)"
    else:
        return f"₹{amount:,.0f} collected — flat 15 points (above ₹1L slab)"
