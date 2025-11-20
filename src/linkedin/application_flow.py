from ai.openai_provider import start_current_job_query_chat
from config import EXCLUDE_COMPANIES
from .constants import timeout_1s, timeout_2s, timeout_5s
from .dom_parser import (
    extract_form_fields,
    extract_form_info,
    extract_step_controls,
    form_state, extract_job_details)
from .form_filler import fill_all_fields
from .job_search import click_job_card


def find_and_click_easy_apply(job_details_section):
    """Finds and clicks the Easy Apply button. Returns (status, message)."""
    if not job_details_section:
        return False, "Job details not found"

    easy_apply_button = job_details_section.query_selector(
        'button[aria-label^="Easy Apply"]'
    )
    if not easy_apply_button:
        applied_message_elem = job_details_section.query_selector(
            ".artdeco-inline-feedback--success .artdeco-inline-feedback__message"
        )
        if applied_message_elem:
            return False, applied_message_elem.inner_text()
        return False, "Easy Apply button not found"
    elif not easy_apply_button.is_enabled():
        return False, "Easy Apply button is DISABLED"

    easy_apply_button.click()
    return True, "Success"


def handle_application_form(page):
    """Handles the multi-step application form. Returns (status, message)."""
    previous_state = None

    while True:
        try:
            application_form = page.wait_for_selector(
                '[class*="easy-apply-modal"], [class^="artdeco-modal"]',
                timeout=timeout_5s,
            )
        except Exception:
            return True, "Application finished"

        if not application_form:
            return False, "Application form not found"

        status, message = process_form_step(page, application_form, previous_state)
        if not status:
            return False, message
        page.wait_for_timeout(timeout_1s)
        previous_state = message  # message contains the form state in this case


def process_form_step(page, application_form, previous_state):
    """Processes a single step of the application form."""
    form_info = extract_form_info(application_form)
    form_fields = extract_form_fields(application_form)
    print(
        f"Extracted form. header: {form_info['header']}, progress: {form_info['progress']}"
    )

    current_state = form_state(form_info, form_fields)
    step_controls = extract_step_controls(application_form)
    if previous_state == current_state:
        print(
            "Form state unchanged from previous step, likely stuck. Dismissing application."
        )
        dismiss_job_apply(page, application_form, step_controls)
        return False, "Form stuck"

    has_errors = any(f.get("hasError", False) for f in form_fields)
    fill_all_fields(page, form_fields, has_errors)

    if not step_controls or not step_controls["nextButton"]:
        print("No next button found in step controls. Dismissing application.")
        dismiss_job_apply(page, application_form, step_controls)
        return False, "No next button"

    page.wait_for_timeout(timeout_2s)
    next_button = page.query_selector(step_controls["nextButton"]["selector"])
    if next_button:
        page.evaluate(
            "el => el.scrollIntoView({ behavior: 'smooth', block: 'center' })",
            next_button,
        )
        page.wait_for_timeout(timeout_1s)
        page.click(
            step_controls["nextButton"]["selector"], timeout=timeout_2s
        )
        page.wait_for_timeout(timeout_1s)

    return True, current_state


def apply_job(page, job):
    """Applies to a job using the Easy Apply button, handling multi-step forms."""
    try:
        if not click_job_card(page, job):
            return False, "Failed to click job card"

        page.wait_for_timeout(timeout_1s)
        job_details_section = page.wait_for_selector(
            'div[class*="job-details"], div[class*="jobs-details"], div[class*="job-view-layout"]',
            timeout=timeout_5s,
        )
        job_details = extract_job_details(job_details_section)
        print(f"Job details: {job_details}")
        company = (job_details['company'] or "").lower()
        if EXCLUDE_COMPANIES and any(excluded.lower() in company for excluded in EXCLUDE_COMPANIES):
            print(f"Skipping {company} due to EXCLUDE_COMPANIES")
            return False, f"Excluded company '{job_details['company']}'"

        status, message = find_and_click_easy_apply(job_details_section)
        if not status:
            return False, message

        page.wait_for_timeout(timeout_1s)
        start_current_job_query_chat(job_details)
        return handle_application_form(page)

    except Exception as e:
        print(f"Error applying to job {getattr(job, 'title', 'Unknown')}: {e}")
        dismiss_job_apply(page, None)
        return False, str(e)


def dismiss_job_apply(page, application_form, step_controls=None):
    """Dismisses the application modal, attempting to discard changes if needed."""
    print("Could not find next button in step controls.")
    if not step_controls and application_form:
        step_controls = extract_step_controls(application_form)

    if step_controls and step_controls["closeButton"]:
        page.click(step_controls["closeButton"]["selector"], timeout=timeout_2s)
        try:
            confirmation_modal = page.wait_for_selector(
                '[role="alertdialog"], [class*="layer-confirmation"]',
                timeout=timeout_5s,
            )
            if confirmation_modal:
                confirmation_controls = extract_step_controls(confirmation_modal)
                if confirmation_controls and confirmation_controls["discardButton"]:
                    page.click(
                        confirmation_controls["discardButton"]["selector"],
                        timeout=timeout_2s,
                    )
                elif confirmation_controls and confirmation_controls["closeButton"]:
                    page.click(
                        confirmation_controls["closeButton"]["selector"],
                        timeout=timeout_2s,
                    )
        except Exception as e:
            print(f"Confirmation modal did not appear or could not discard: {e}")
    else:
        print("Could not find cancel button in step controls.")
