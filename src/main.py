import sys

from playwright.sync_api import sync_playwright

from config import HIDE_BROWSER, OPEN_MAXIMIZED, JOB_KEYWORDS, JOB_LOCATION
from linkedin.constants import timeout_1s
from linkedin.easy_apply import apply_jobs_easy_apply, easy_apply_by_url
from linkedin.login import login


def main():
    with sync_playwright() as p:
        print("Starting JobApplier.AI...")
        job_urls = sys.argv[1:]
        args = ["--start-maximized"] if OPEN_MAXIMIZED else []
        browser = p.chromium.launch(headless=HIDE_BROWSER, args=args)
        page, logged_in = login(browser, save_login=True)
        if logged_in:
            if job_urls:
                print(f"Applying given {len(job_urls)} jobs urls")
                easy_apply_by_url(page, job_urls)
            else:
                print(f"Applying jobs: '{JOB_KEYWORDS}' and location: '{JOB_LOCATION}'")
                apply_jobs_easy_apply(page, JOB_KEYWORDS, JOB_LOCATION)
        else:
            print("Login failed. Exiting.")
        page.wait_for_timeout(timeout_1s)
        browser.close()

if __name__ == "__main__":
    main()
