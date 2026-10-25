import datetime

from openai import RateLimitError, OpenAIError

from config import JOB_URLS_FILE
from utils.run_data_manager import update_run_data_job_applications
from utils.txt_utils import remove_line_from
from .application_flow import apply_job, dismiss_job_apply
from .constants import timeout_5s, timeout_2s
from .job_search import fetch_job_list, click_job_card


def easy_apply_by_url(page, job_urls):
    """Performs the Easy Apply process given the list of job URLs."""
    for job_url in job_urls:
        page.goto(job_url)
        page.wait_for_timeout(timeout_5s)
        applied, status = apply_job(page, True)
        print(f"Job URL: {job_url}, applied: {applied}, status: {status}")
        if applied:
            remove_line_from(JOB_URLS_FILE, job_url)

def apply_jobs_easy_apply(page, keywords, location):
    """Performs the Easy Apply process for jobs on LinkedIn."""
    job_search = f"{keywords} in {location}"
    print(f"Searching for jobs: {job_search}")
    page.goto("https://www.linkedin.com/jobs/")
    search_input = page.locator(
        'input[componentkey="jobSearchBox"], input[placeholder="Describe the job you want"]'
    ).first
    search_input.fill(job_search)
    search_input.press("Enter")
    page.wait_for_url("**/jobs/search-results/**", timeout=timeout_5s)
    page.wait_for_timeout(timeout_5s)
    easy_apply_filter = page.locator(
        'div[aria-label="Filter by Easy Apply"]:visible label'
    ).first
    if not easy_apply_filter.count():
        easy_apply_filter = page.locator(
            'label:has-text("Easy Apply"):visible'
        ).first
    page.wait_for_timeout(timeout_2s)
    if easy_apply_filter.count():
        easy_apply_filter.click()
    else:
        print("Easy Apply filter not found. Continuing without filter.")
    page.wait_for_timeout(timeout_5s)

    current_page = 1
    next_page_selector = (
        'button[data-testid="pagination-controls-next-button-visible"]:visible, '
        'button[aria-label="View next page"]:visible'
    )
    jobs_applied = 0
    job_application_id = f"{'_'.join(keywords.split())}_{location}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    update_run_data_job_applications(job_application_id, keywords, location, current_page)
    while True:
        print(f"Current page: ({current_page})")
        print("Fetching job listings.")
        # Close any open job apply popups before clicking the next job card
        dismiss_job_apply(page, None)
        page.wait_for_timeout(timeout_2s)
        jobs = fetch_job_list(page)
        if not jobs:
            print("No more job listings found. Ending process.")
            break
        print(f"Found {len(jobs)} jobs on the current page.")
        for job in jobs:
            try:
                # Close any open job apply popups before clicking the next job card
                dismiss_job_apply(page, None)
                if not click_job_card(page, job):
                    return False, "Failed to click job card"
                page.wait_for_timeout(timeout_2s)
                applied, status = apply_job(page)
                if applied:
                    jobs_applied += 1
                    print("Successfully applied: ", jobs_applied)
                elif "limit" in status:
                    print(f"Alert: {status}\nEasy Apply limit reached. Stopping application process!!")
                    update_run_data_job_applications(job_application_id,
                                                     keywords,
                                                     location,
                                                     current_page,
                                                     applied,
                                                     "Easy Apply limit reached")
                    return None
                else:
                    print(f"Failed to apply. Status: {status}")
                update_run_data_job_applications(job_application_id, keywords, location, current_page, applied, status)
            except RateLimitError as e:
                print("Rate limit exceeded:", e)
                return False, "OpenAI Rate limit exceeded"
            except OpenAIError as e:
                print("Any OpenAI-related error:", e)
                return False, "OpenAI error"
            except Exception as e:
                print(f"Error applying the job: {e}")
            finally:
                dismiss_job_apply(page, None)
        print(f"Page ({current_page}) finished.")
        next_page_button = page.locator(next_page_selector).first
        if next_page_button.count() and next_page_button.is_enabled():
            print("Moving to next page...")
            active_page_button = page.locator(
                'button[aria-current="true"][aria-label^="Page "]'
            ).first
            previous_page_label = (
                active_page_button.get_attribute("aria-label")
                if active_page_button.count()
                else None
            )
            next_page_button.click()
            if previous_page_label:
                page.wait_for_function(
                    """previousLabel => {
                        const activePage = document.querySelector(
                            'button[aria-current="true"][aria-label^="Page "]'
                        );
                        return activePage
                            && activePage.getAttribute("aria-label") !== previousLabel;
                    }""",
                    arg=previous_page_label,
                    timeout=timeout_5s,
                )
                active_page_label = page.locator(
                    'button[aria-current="true"][aria-label^="Page "]'
                ).first.get_attribute("aria-label")
                current_page = (
                    int(active_page_label.rsplit(" ", 1)[-1])
                    if active_page_label
                    else current_page + 1
                )
            else:
                page.wait_for_timeout(timeout_2s)
                current_page += 1
        else:
            print("No more pages for job search list found. Ending process.")
            break
