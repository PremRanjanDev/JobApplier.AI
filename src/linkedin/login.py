import os
import pathlib

LINKEDIN_STATE_FILE = "user_data/linkedin_state.json"

def login(browser, save_login=False):
    """Logs in to LinkedIn using the provided browser object.
    Restores session state if available, saves it if requested.
    Returns (page, True) if logged in, (page, False) otherwise."""

    context_args = {}
    if os.path.exists(LINKEDIN_STATE_FILE):
        context_args["storage_state"] = LINKEDIN_STATE_FILE
        print("Restoring LinkedIn session from saved state...")

    context = browser.new_context(**context_args)
    page = context.new_page()

    print("Navigating to LinkedIn feed...")
    page.goto("https://www.linkedin.com/feed/")

    current_url = page.url
    if "/feed" in current_url:
        print("Already logged in to LinkedIn.")
        return page, True
    else:
        print("Not logged in. Please log in manually in the opened browser window.")
        page.goto("https://www.linkedin.com/login")
        try:
            page.wait_for_url("https://www.linkedin.com/feed/", timeout=120000)
            print("Login successful.")
            if save_login:
                pathlib.Path(os.path.dirname(LINKEDIN_STATE_FILE)).mkdir(parents=True, exist_ok=True)
                print("Saving state...")
                page.context.storage_state(path=LINKEDIN_STATE_FILE)
                print(f"Login state saved to {LINKEDIN_STATE_FILE}")
            return page, True
        except Exception as e:
            print(f"Login failed or timed out: {e}")
            return page, False
