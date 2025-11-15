from playwright.sync_api import sync_playwright

from config import HIDE_BROWSER, OPEN_MAXIMIZED, JOB_KEYWORDS, JOB_LOCATION
from linkedin.easy_apply import apply_jobs_easy_apply
from linkedin.login import login


def main():
    with sync_playwright() as p:
        args = ["--start-maximized"] if OPEN_MAXIMIZED else []
        browser = p.chromium.launch(headless=HIDE_BROWSER, args=args)
        page, logged_in = login(browser, save_login=True)
        if logged_in:
            apply_jobs_easy_apply(page, JOB_KEYWORDS, JOB_LOCATION)
        else:
            print("Login failed. Exiting.")
        page.wait_for_timeout(10000)
        browser.close()

if __name__ == "__main__":
    main()
