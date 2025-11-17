import datetime
from utils.run_data_manager import update_run_data_job_applications
from .application_flow import apply_job
from .constants import timeout_2s
from .job_search import fetch_job_list

def apply_jobs_easy_apply(page, keywords, location):
    """Performs the Easy Apply process for jobs on LinkedIn."""
    print("Starting the Easy Apply process...")
    print(f"Searching for jobs: {keywords} in {location}")
    page.goto(f"https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}&f_AL=true")
    current_page = 1
    next_page_selector = 'button[aria-label="View next page"]'
    jobs_applied = 0
    job_application_id = f"{'_'.join(keywords.split())}_{location}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    update_run_data_job_applications(job_application_id, keywords, location, current_page)
    while True:
        print("Fetching job listings.")
        page.wait_for_timeout(timeout_2s)
        jobs = fetch_job_list(page)
        if not jobs:
            print("No more job listings found. Ending process.")
            break
        print(f"Found {len(jobs)} jobs on the current page.")
        for job in jobs:
            print("Processing job...")
            job_id = job.get_attribute("data-job-id")
            print(f"Job ID: {job_id}")

            applied, status = apply_job(page, job)
            if applied:
                jobs_applied += 1
                print("Successfully applied: ", jobs_applied)
            else:
                print(f"Failed to apply. Status: {status}")
            update_run_data_job_applications(job_application_id, keywords, location, current_page, applied, status)
        print(f"Current page '{current_page}' finished.")
        next_page_button = page.query_selector(next_page_selector)
        if next_page_button:
            print("Moving to next page...")
            next_page_button.click()
            page.wait_for_timeout(timeout_2s)
            current_page = page.query_selector('button[aria-current="page"][class*="button--active"] span').inner_text()
        else:
            print("No more pages for job search list found. Ending process.")
            break
