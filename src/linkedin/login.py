import json
import os

from linkedin.constants import timeout_1s


def login(page, saved_state_file=None):
    """Logs in to LinkedIn on the given page.
    The session is kept in the Chrome profile, so manual login is needed at most once.
    If not logged in, cookies from saved_state_file (if given and present) are tried first.
    Returns True if logged in, False otherwise."""
    print("Starting LinkedIn login process...")
    page.wait_for_timeout(timeout_1s)
    print("Navigating to LinkedIn feed...")
    page.goto("https://www.linkedin.com/feed/")

    if "/feed" in page.url:
        print("Already logged in.")
        return True

    if saved_state_file and os.path.exists(saved_state_file):
        print("Importing saved LinkedIn session...")
        with open(saved_state_file) as f:
            page.context.add_cookies(json.load(f).get("cookies", []))
        page.goto("https://www.linkedin.com/feed/")
        if "/feed" in page.url:
            print("Already logged in.")
            return True

    print("Not logged in. Please authenticate manually...")
    page.goto("https://www.linkedin.com/login")

    try:
        page.wait_for_url("https://www.linkedin.com/feed/", timeout=120_000)
        print("Login successful.")
        return True
    except Exception as e:
        print(f"Login failed: {e}")
        return False
