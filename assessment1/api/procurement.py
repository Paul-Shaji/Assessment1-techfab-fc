import frappe
from frappe.utils import nowdate


def create_material_request_on_so_submit(doc, method=None):
    shortage_items = []

    for so_item in doc.items:
        warehouse = so_item.warehouse or doc.set_warehouse or ""

        if not warehouse:
            frappe.log_error(
                f"No warehouse found for item {so_item.item_code}. Skipping.",
                "Material Request Creation"
            )
            continue

        bin_data = frappe.db.get_value(
            "Bin",
            {"item_code": so_item.item_code, "warehouse": warehouse},
            ["actual_qty", "reserved_qty"],
            as_dict=True
        )

        actual_qty   = bin_data.actual_qty if bin_data else 0
        reserved_qty = bin_data.reserved_qty if bin_data else 0

        # available = what is physically in stock minus what is already promised
        available_qty = actual_qty - reserved_qty

        # reserved_qty already includes this SO because it was just submitted
        # so available_qty is correctly reduced for this SO already
        shortage_qty = so_item.qty - available_qty

        if shortage_qty > 0:
            shortage_items.append({
                "item_code": so_item.item_code,
                "item_name": so_item.item_name,
                "qty": shortage_qty,
                "uom": so_item.uom,
                "warehouse": warehouse,
            })

    if not shortage_items:
        frappe.msgprint(
            "All items are sufficiently stocked. No Material Request created."
        )
        return

    mr = frappe.get_doc({
        "doctype": "Material Request",
        "material_request_type": "Purchase",
        "transaction_date": nowdate(),
        "schedule_date": nowdate(),
        "company": doc.company,
        "items": [
            {
                "item_code": item["item_code"],
                "item_name": item["item_name"],
                "qty": item["qty"],
                "uom": item["uom"],
                "warehouse": item["warehouse"],
                "schedule_date": nowdate(),
            }
            for item in shortage_items
        ],
    })
    mr.insert(ignore_permissions=True)
    mr.submit()

    frappe.msgprint(
        f"Material Request <b>{mr.name}</b> created for "
        f"<b>{len(shortage_items)}</b> shortage item(s).",
        alert=True
    )

    notify_purchase_team(doc.name, mr.name, shortage_items)


def notify_purchase_team(so_name, mr_name, shortage_items):
    try:
        purchase_users = frappe.get_all(
            "Has Role",
            filters={
                "role": ["in", ["Purchase Manager", "Purchase User"]],
                "parenttype": "User"
            },
            fields=["parent"],
            distinct=True
        )

        recipients = []
        for u in purchase_users:
            user = frappe.db.get_value(
                "User",
                u.parent,
                ["email", "user_type"],
                as_dict=True
            )
            if user and user.email and user.user_type == "System User":
                recipients.append(user.email)

        if not recipients:
            frappe.log_error(
                "No purchase team recipients found",
                "Material Request Notification"
            )
            return

        rows = "".join(
            f"<tr><td>{i['item_code']}</td><td>{i['item_name']}</td>"
            f"<td>{i['qty']}</td><td>{i['uom']}</td></tr>"
            for i in shortage_items
        )

        frappe.sendmail(
            recipients=recipients,
            subject=f"[TechFab] Raw Material Shortage — {so_name}",
            message=f"""
                <p>Material Request <b>{mr_name}</b> has been automatically
                created from Sales Order <b>{so_name}</b> due to insufficient
                stock.</p>
                <table border="1" cellpadding="5" cellspacing="0">
                    <thead>
                        <tr>
                            <th>Item Code</th><th>Item Name</th>
                            <th>Shortage Qty</th><th>UOM</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>
                <p>Please raise a Purchase Order at the earliest.</p>
            """,
            now=False
        )

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Purchase Team Email Failed")
