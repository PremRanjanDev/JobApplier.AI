from playwright.sync_api import sync_playwright

from config import CHROME_PROFILE_DIR, LINKEDIN_STATE_FILE, DEFAULT_CHROME_USER_DATA_DIR, USE_DEFAULT_CHROME, HIDE_BROWSER, \
    OPEN_MAXIMIZED, JOB_KEYWORDS, JOB_LOCATION, JOB_URLS_FILE
from linkedin.constants import timeout_1s, timeout_2s
from linkedin.easy_apply import apply_jobs_easy_apply, easy_apply_by_url
from linkedin.login import login
from utils.user_data_manager import read_header_file


def connect_default_chrome(p):
    """Attaches to the running everyday Chrome via the endpoint it publishes when
    remote debugging is allowed at chrome://inspect/#remote-debugging."""
    port_file = DEFAULT_CHROME_USER_DATA_DIR / "DevToolsActivePort"
    try:
        port, ws_path = port_file.read_text().split("\n")[:2]
    except FileNotFoundError:
        raise RuntimeError("Chrome remote debugging is not enabled. Open Chrome, go to "
                           "chrome://inspect/#remote-debugging and allow remote debugging, then retry.")
    except PermissionError:
        raise RuntimeError(f"macOS blocked reading {port_file}. Give your terminal app Full Disk Access in "
                           "System Settings > Privacy & Security > Full Disk Access, restart it, then retry.")
    browser = p.chromium.connect_over_cdp(f"ws://127.0.0.1:{port.strip()}{ws_path.strip()}")
    return browser.contexts[0]


def launch_app_chrome(p):
    """Launches Chrome with the app's own persistent profile."""
    args = ["--start-maximized"] if OPEN_MAXIMIZED else []
    # Persistent profile keeps logins, cookies and installed extensions across runs
    return p.chromium.launch_persistent_context(
        CHROME_PROFILE_DIR,
        channel="chrome",
        headless=HIDE_BROWSER,
        args=args,
        no_viewport=True,
        chromium_sandbox=True,  # avoids Playwright's default --no-sandbox flag
        ignore_default_args=["--disable-extensions"],
    )


def main():
    with sync_playwright() as p:
        print("Starting JobApplier.AI...")
        if USE_DEFAULT_CHROME:
            context = connect_default_chrome(p)
            page = context.new_page()
            logged_in = login(page)
        else:
            context = launch_app_chrome(p)
            page = context.pages[0] if context.pages else context.new_page()
            logged_in = login(page, saved_state_file=LINKEDIN_STATE_FILE)
        if logged_in:
            _, job_urls = read_header_file(JOB_URLS_FILE, 5)
            valid_job_urls = [u for u in job_urls if u.startswith("https://")]
            if valid_job_urls:
                print(f"Applying given {len(valid_job_urls)} valid jobs urls")
                page.wait_for_timeout(timeout_2s)
                easy_apply_by_url(page, valid_job_urls)
            else:
                print(f"Applying jobs: '{JOB_KEYWORDS}' and location: '{JOB_LOCATION}'")
                apply_jobs_easy_apply(page, JOB_KEYWORDS, JOB_LOCATION)
        else:
            print("Login failed. Exiting.")
        page.wait_for_timeout(timeout_1s)
        if USE_DEFAULT_CHROME:
            page.close()  # leave the user's Chrome and other tabs open
        else:
            context.close()

if __name__ == "__main__":
    main()
