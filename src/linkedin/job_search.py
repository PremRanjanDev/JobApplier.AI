from .constants import timeout_5s


def fetch_job_list(page):
    """Fetches job listings from LinkedIn based on job title and location."""
    jobs = page.query_selector_all(".job-card-container--clickable")

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
        jobs = page.query_selector_all(".job-card-container--clickable")

    return jobs


def click_job_card(page, job):
    """Clicks on a job card and returns success status."""
    job_id = job.get_attribute("data-job-id")
    if not job_id:
        print("Job element does not have a data-job-id attribute.")
        return False

    job_selector = f'.job-card-container--clickable[data-job-id="{job_id}"]'
    fresh_job = page.query_selector(job_selector)
    if not fresh_job:
        print(f"Could not find job element with selector: {job_selector}")
        return False

    fresh_job.click(timeout=timeout_5s)
    return True
