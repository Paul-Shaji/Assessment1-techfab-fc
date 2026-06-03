import frappe


def validate_material_availability(doc, method=None):
    """
    Runs on_submit of Work Order.
    Checks if required raw materials are available in the
    source warehouse before allowing production to start.
    Blocks submission if any material is insufficient.
    """
    if not doc.required_items:
        return

    shortage_lines = []

    for row in doc.required_items:
        warehouse = (
          doc.source_warehouse
          or row.source_warehouse
          or frappe.db.get_value(
              "Item Default",
              {"parent": row.item_code, "company": doc.company},
              "default_warehouse"
          )
          or ""
        )
        if not warehouse:
            frappe.throw(
                f"Source Warehouse not set on Work Order or item {row.item_code}. "
                "Please set it before submitting."
            )

        bin_data = frappe.db.get_value(
            "Bin",
            {"item_code": row.item_code, "warehouse": warehouse},
            ["actual_qty", "reserved_qty"],
            as_dict=True
        )

        actual_qty   = bin_data.actual_qty if bin_data else 0
        reserved_qty = bin_data.reserved_qty if bin_data else 0
        available_qty = actual_qty - reserved_qty
        required_qty  = row.required_qty

        if available_qty < required_qty:
            shortage_lines.append(
                f"<tr>"
                f"<td>{row.item_code}</td>"
                f"<td>{row.item_name}</td>"
                f"<td>{required_qty}</td>"
                f"<td>{available_qty}</td>"
                f"<td>{required_qty - available_qty}</td>"
                f"</tr>"
            )

    if shortage_lines:
        rows_html = "".join(shortage_lines)
        frappe.throw(
            f"""
            <p>Cannot start production. The following raw materials
            are insufficient in <b>{doc.source_warehouse}</b>:</p>
            <table border="1" cellpadding="5" cellspacing="0">
                <thead>
                    <tr>
                        <th>Item Code</th>
                        <th>Item Name</th>
                        <th>Required</th>
                        <th>Available</th>
                        <th>Shortage</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
            <p>Please ensure a Purchase Order is raised and
            materials are received before starting production.</p>
            """,
            title="Insufficient Raw Materials"
        )
