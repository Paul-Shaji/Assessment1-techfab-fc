import frappe
import requests
from frappe import _


@frappe.whitelist(allow_guest=True)
def google_auth_redirect():
    """
    Step 1: Build the Google OAuth URL and redirect the user there.
    Called when user clicks 'Sign in with Google'.
    """
    import urllib.parse

    social_login_key = frappe.get_doc("Social Login Key", "google")
    client_id = social_login_key.client_id

    params = urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": frappe.utils.get_url("/api/method/gauth.api.google_auth_callback"),
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
    })

    auth_url = f"https://accounts.google.com/o/oauth2/auth?{params}"

    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = auth_url


@frappe.whitelist(allow_guest=True)
def google_auth_callback(code=None, error=None):
    """
    Step 2: Google redirects back here with a code.
    Exchange it for user info, log them in, redirect to /shop.
    """

    if error or not code:
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = "/store-login?error=google_denied"
        return

    social_login_key = frappe.get_doc("Social Login Key", "google")
    client_id = social_login_key.client_id
    client_secret = social_login_key.get_password("client_secret")

    # Exchange code for access token
    token_response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": frappe.utils.get_url("/api/method/gauth.api.google_auth_callback"),
            "grant_type": "authorization_code",
        }
    )

    if token_response.status_code != 200:
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = "/store-login?error=token_failed"
        return

    token_data = token_response.json()
    access_token = token_data.get("access_token")

    # Get user info from Google
    user_info_response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if user_info_response.status_code != 200:
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = "/store-login?error=userinfo_failed"
        return

    info = user_info_response.json()
    email = info.get("email")
    first_name = info.get("given_name", email)
    last_name = info.get("family_name", "")
    full_name = info.get("name", email)

    if not email:
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = "/store-login?error=no_email"
        return

    # Find or create Frappe User
    if not frappe.db.exists("User", email):
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "user_type": "Website User",
            "send_welcome_email": 0,
            "enabled": 1,
        })
        user.insert(ignore_permissions=True)
        frappe.db.commit()

    # Find or create Customer
    if not frappe.db.exists("Customer", {"email_id": email}):
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": full_name,
            "email_id": email,
            "customer_type": "Individual",
            "customer_group": "Individual",
            "territory": "All Territories",
        })
        customer.insert(ignore_permissions=True)
        frappe.db.commit()

    # Log the user in and redirect to shop
    frappe.local.login_manager.login_as(email)

    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = "/shop"