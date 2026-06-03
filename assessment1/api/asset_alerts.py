import frappe
from frappe.utils import nowdate, add_days, getdate


# Alert is sent only on these exact days before due date
ALERT_DAYS_BEFORE = [30, 7, 0]


def send_maintenance_alerts():
    """
    Scheduled daily job.
    Sends alert only on exact checkpoints: 30 days before,
    7 days before, and on the due date itself.
    Maximum 3 emails per asset per maintenance cycle.
    """
    today = getdate(nowdate())

    # Build list of exact target dates we care about today
    target_dates = [add_days(today, days) for days in ALERT_DAYS_BEFORE]

    due_tasks = frappe.db.sql("""
        SELECT
            am.asset_name,
            amt.maintenance_task,
            amt.maintenance_type,
            amt.next_due_date,
            amt.last_completion_date,
            a.location
        FROM `tabAsset Maintenance Task` amt
        INNER JOIN `tabAsset Maintenance` am ON am.name = amt.parent
        LEFT JOIN `tabAsset` a ON a.name = am.asset_name
        WHERE
            amt.next_due_date IN %(target_dates)s
        ORDER BY amt.next_due_date ASC
    """, {"target_dates": target_dates}, as_dict=True)

    if not due_tasks:
        return

    recipients = get_alert_recipients()

    if not recipients:
        frappe.log_error(
            "No recipients found for asset maintenance alerts",
            "Asset Maintenance Alert"
        )
        return

    rows = "".join(
        f"<tr>"
        f"<td>{t.asset_name}</td>"
        f"<td>{t.location or '-'}</td>"
        f"<td>{t.maintenance_task or '-'}</td>"
        f"<td>{t.maintenance_type}</td>"
        f"<td>{t.next_due_date}</td>"
        f"<td>{'<b style=color:red>TODAY</b>' if getdate(t.next_due_date) == today else str((getdate(t.next_due_date) - today).days) + ' days'}</td>"
        f"<td>{t.last_completion_date or 'Never'}</td>"
        f"</tr>"
        for t in due_tasks
    )

    frappe.sendmail(
        recipients=recipients,
        subject=f"[TechFab] Asset Maintenance Reminder — {len(due_tasks)} Item(s)",
        message=f"""
            <p>This is an automated maintenance reminder for the following assets:</p>
            <table border="1" cellpadding="5" cellspacing="0" style="width:100%">
                <thead style="background:#f5f5f5">
                    <tr>
                        <th>Asset</th>
                        <th>Location</th>
                        <th>Task</th>
                        <th>Type</th>
                        <th>Due Date</th>
                        <th>Due In</th>
                        <th>Last Done</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
            <p>Alerts are sent 30 days before, 7 days before,
            and on the due date.</p>
        """,
        now=False
    )


def get_alert_recipients():
    roles = ["System Manager", "HR Manager", "Manufacturing Manager"]
    users = frappe.get_all(
        "Has Role",
        filters={
            "role": ["in", roles],
            "parenttype": "User"
        },
        fields=["parent"],
        distinct=True
    )

    recipients = []
    for u in users:
        user = frappe.db.get_value(
            "User",
            u.parent,
            ["email", "user_type"],
            as_dict=True
        )
        if user and user.email and user.user_type == "System User":
            recipients.append(user.email)

    return recipients
