from playwright.sync_api import sync_playwright

from config import HIDE_BROWSER, OPEN_MAXIMIZED
from linkedin.easy_apply import apply_jobs_easy_apply
from linkedin.login import login


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HIDE_BROWSER,
                                    args=[flag for flag in ["--start-maximized"] if OPEN_MAXIMIZED])
        page, logged_in = login(browser, save_login=True)
        if logged_in:
            apply_jobs_easy_apply(page, "Java react", "Singapore")
        else:
            print("Login failed. Exiting.")
        page.wait_for_timeout(10000)  # Keep open for 10 seconds as an example
        browser.close()

if __name__ == "__main__":
    main()
