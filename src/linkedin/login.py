import os
import pathlib

from config import LINKEDIN_STATE_FILE


def login(browser, save_login=False):
    """Logs in to LinkedIn using the provided browser object.
    Restores session state if available, saves it if requested.
    Returns (page, True) if logged in, (page, False) otherwise."""
    print("Starting LinkedIn login process...")
    context_args = {"no_viewport": True}
    if os.path.exists(LINKEDIN_STATE_FILE):
        print("LinkedIn session state found, restoring...")
        context_args["storage_state"] = LINKEDIN_STATE_FILE

    context = browser.new_context(**context_args)
    page = context.new_page()
    print("Navigating to LinkedIn feed...")
    page.goto("https://www.linkedin.com/feed/")

    if "/feed" in page.url:
        print("Already logged in.")
        return page, True

    print("Not logged in. Please authenticate manually...")
    page.goto("https://www.linkedin.com/login")

    try:
        page.wait_for_url("https://www.linkedin.com/feed/", timeout=120_000)
        print("Login successful.")
        if save_login:
            pathlib.Path(os.path.dirname(LINKEDIN_STATE_FILE)).mkdir(parents=True, exist_ok=True)
            page.context.storage_state(path=LINKEDIN_STATE_FILE)
            print("Session saved.")
        return page, True
    except Exception as e:
        print(f"Login failed: {e}")
        return page, False
