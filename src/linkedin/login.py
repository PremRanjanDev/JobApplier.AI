import os
import pathlib

LINKEDIN_STATE_FILE = "user_data/linkedin_state.json"

def login(p, save_login=False):
    """Logs in to LinkedIn if needed and returns the browser and page objects.
    Optionally saves the browser state for future sessions."""
    browser = p.chromium.launch(
        headless=False,
        args=["--start-maximized"]
    )
    context_args = {"viewport": {"width": 1920, "height": 1080}}
    if os.path.exists(LINKEDIN_STATE_FILE):
        context_args["storage_state"] = LINKEDIN_STATE_FILE
    context = browser.new_context(**context_args)
    page = context.new_page()
    print("Navigating to LinkedIn feed...")
    page.goto("https://www.linkedin.com/feed/")

    # Check if logged in by verifying the URL and optionally a user-specific selector
    current_url = page.url
    if "/feed" in current_url:
        print("Already logged in to LinkedIn.")
    else:
        print("Not logged in. Please log in manually in the opened browser window.")
        page.goto("https://www.linkedin.com/login")
        page.wait_for_url("https://www.linkedin.com/feed/", timeout=120000)  # Wait for up to 120 seconds until logged in
        print("Login successful.")
        if save_login:
            pathlib.Path(os.path.dirname(LINKEDIN_STATE_FILE)).mkdir(parents=True, exist_ok=True)
            print("Saving state...")
            context.storage_state(path=LINKEDIN_STATE_FILE)
            print(f"Login state saved to {LINKEDIN_STATE_FILE}")

    return browser, page
