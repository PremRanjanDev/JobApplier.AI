from playwright.sync_api import sync_playwright

from config import HIDE_BROWSER, OPEN_MAXIMIZED, JOB_KEYWORDS, JOB_LOCATION, JOB_URLS_FILE
from linkedin.constants import timeout_1s
from linkedin.easy_apply import apply_jobs_easy_apply, easy_apply_by_url
from linkedin.login import login
from utils.user_data_manager import read_header_file


def main():
    with sync_playwright() as p:
        print("Starting JobApplier.AI...")
        args = ["--start-maximized"] if OPEN_MAXIMIZED else []
        browser = p.chromium.launch(headless=HIDE_BROWSER, args=args)
        page, logged_in = login(browser, save_login=True)
        if logged_in:
            _, job_urls = read_header_file(JOB_URLS_FILE, 5)
            valid_job_urls = [u for u in job_urls if u.startswith("https://")]
            if valid_job_urls:
                print(f"Applying given {len(job_urls)} valid jobs urls")
                easy_apply_by_url(page, valid_job_urls)
            else:
                print(f"Applying jobs: '{JOB_KEYWORDS}' and location: '{JOB_LOCATION}'")
                apply_jobs_easy_apply(page, JOB_KEYWORDS, JOB_LOCATION)
        else:
            print("Login failed. Exiting.")
        page.wait_for_timeout(timeout_1s)
        browser.close()

if __name__ == "__main__":
    main()
