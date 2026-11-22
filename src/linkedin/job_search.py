from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from .constants import timeout_5s

job_card_selector = (
    ".job-card-container--clickable, .job-search-card, "
    'main [role="button"][componentkey^="job-card-component-ref-"]'
)


def fetch_job_list(page):
    """Fetches job listings from LinkedIn based on job title and location."""
    try:
        page.wait_for_selector(job_card_selector, timeout=timeout_5s)
    except PlaywrightTimeoutError:
        print(f"No job cards matching {job_card_selector} appeared within {timeout_5s} ms.")
        return []

    jobs = page.query_selector_all(job_card_selector)

    prev_job_len = 0
    while len(jobs) != prev_job_len:
        print(f"Found {len(jobs)} jobs, scrolling to load more...")
        prev_job_len = len(jobs)
        # Scroll the last job card into the center of the viewport for better visibility/loading
        page.evaluate(
            '(el) => el.scrollIntoView({behavior: "smooth", block: "start"})',
            jobs[-1],
        )
        page.wait_for_timeout(800)  # Wait for more jobs to load
        jobs = page.query_selector_all(job_card_selector)

    return jobs


def click_job_card(page, job):
    """Clicks on a job card and returns success status."""
    job.click(timeout=timeout_5s)
    return True
