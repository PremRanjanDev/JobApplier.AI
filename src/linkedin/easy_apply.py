from utils.qna_manager import get_text_answer, get_select_answer
from .dom_parser import extract_form_fields, extract_form_info, extract_step_controls, form_state

timeout_5s = 5000 # 5 seconds timeout for waiting for controls
timeout_2s = 2000 # 2 seconds timeout for waiting for clicks
timeout_1s = 1000 # 1 seconds timeout for waiting extra


def apply_jobs_easy_apply(page, keywords, location):
    """Performs the Easy Apply process for a jobs on LinkedIn."""
    print("Starting the Easy Apply process...")
    print(f"Searching for jobs: {keywords} in {location}")
    page.goto(f"https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}&f_AL=true")
    next_page_selector = 'button[aria-label="View next page"]'
    while True:
        print(f"Fetching job listings.")
        jobs = fetch_job_list(page)
        if not jobs:
            print("No more job listings found. Ending process.")
            break
        print(f"Found {len(jobs)} jobs on the current page.")
        for job in jobs:
            print("Processing job...")
            job_id = job.get_attribute('data-job-id')
            print(f"Job ID: {job_id}")

            applied, status = apply_job(page, job)
            if applied:
                print("Successfully applied.")
            else:
                print(f"Failed to apply. Status: {status}")
        current_page = page.query_selector('button[aria-current="page"][class*="button--active"] span').inner_text()
        print(f"Current page '{current_page}' completed.")
        next_page_button = page.query_selector(next_page_selector)
        if next_page_button:
            print("Moving to next page...")
            next_page_button.click()
            page.wait_for_timeout(timeout_2s)
        else:
            print("No more pages for job search list found. Ending process.")
            break


def fetch_job_list(page):
    """Fetches job listings from LinkedIn based on job title and location."""
    jobs = page.query_selector_all('.job-card-container--clickable')

    prev_job_len = 0
    while len(jobs) != prev_job_len:
        print(f"Found {len(jobs)} jobs, scrolling to load more...")
        prev_job_len = len(jobs)
        # Scroll the last job card into the center of the viewport for better visibility/loading
        page.evaluate(
            '(el) => el.scrollIntoView({behavior: "smooth", block: "start"})',
            jobs[-1]
        )
        page.wait_for_timeout(800)  # Wait for more jobs to load
        jobs = page.query_selector_all('.job-card-container--clickable')
    
    return jobs

def click_job_card(page, job):
    """Clicks on a job card and returns success status."""
    job_id = job.get_attribute('data-job-id')
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

def find_and_click_easy_apply(job_details_section):
    """Finds and clicks the Easy Apply button. Returns status and message."""
    if not job_details_section:
        return False, "Job details not found"

    easy_apply_button = job_details_section.query_selector('button[aria-label^="Easy Apply"]')
    if not easy_apply_button:
        applied_message_elem = job_details_section.query_selector('.artdeco-inline-feedback--success .artdeco-inline-feedback__message')
        if applied_message_elem:
            return False, "Already applied"
        return False, "Easy Apply button not found"
    elif not easy_apply_button.is_enabled():
        return False, "Easy Apply button is DISABLED"
    
    easy_apply_button.click()
    return True, "Success"

def handle_application_form(page):
    """Handles the multi-step application form. Returns application status and message."""
    previous_state = None
    
    while True:
        try:
            application_form = page.wait_for_selector(
                '[class*="easy-apply-modal"], [class^="artdeco-modal"]',
                timeout=timeout_5s
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
    print(f"Extracted form. header: {form_info['header']}, progress: {form_info['progress']}")

    current_state = form_state(form_info, form_fields)
    step_controls = extract_step_controls(application_form)
    if previous_state == current_state:
        print("Form state unchanged from previous step, likely stuck. Dismissing application.")
        dismiss_job_apply(page, application_form, step_controls)
        return False, "Form stuck"

    has_errors = any(f.get('hasError', False) for f in form_fields)
    fill_all_fields(page, form_fields, has_errors)
    
    if not step_controls or not step_controls['nextButton']:
        print("No next button found in step controls. Dismissing application.")
        dismiss_job_apply(page, application_form, step_controls)
        return False, "No next button"

    page.wait_for_timeout(timeout_2s)
    next_button = page.query_selector(step_controls['nextButton']['selector'])
    if next_button:
        page.evaluate('el => el.scrollIntoView({ behavior: "smooth", block: "center" })', next_button)
        page.wait_for_timeout(timeout_1s)
        page.click(step_controls['nextButton']['selector'], timeout=timeout_2s)
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
            timeout=timeout_5s
        )
        status, message = find_and_click_easy_apply(job_details_section)
        if not status:
            return False, message
        
        page.wait_for_timeout(timeout_1s)
        return handle_application_form(page)
        
    except Exception as e:
        print(f"Error applying to job {getattr(job, 'title', 'Unknown')}: {e}")
        dismiss_job_apply(page, None)
        return False, str(e)

def dismiss_job_apply(page, application_form, step_controls=None):
    print("Could not find next button in step controls.")
    if not step_controls:
        step_controls = extract_step_controls(application_form)
    
    if step_controls and step_controls['closeButton']:
        page.click(step_controls['closeButton']['selector'], timeout=timeout_2s)
        try:
            confirmation_modal = page.wait_for_selector(
                '[role="alertdialog"], [class*="layer-confirmation"]',
                timeout=timeout_5s
            )
            if confirmation_modal:
                confirmation_controls = extract_step_controls(confirmation_modal)
                if confirmation_controls and confirmation_controls['discardButton']:
                     page.click(confirmation_controls['discardButton']['selector'], timeout=timeout_2s)
                elif confirmation_controls and confirmation_controls['closeButton']:
                    page.click(confirmation_controls['closeButton']['selector'], timeout=timeout_2s)
        except Exception as e:
            print(f"Confirmation modal did not appear or could not discard: {e}")
    else:
        print("Could not find cancel button in step controls.") # Indicate failure

def fill_all_fields(page, input_fields, has_errors=False):
    """Fills out all fields in the application form based on the provided input_fields.
    If form_element (ElementHandle) is provided, actions will try to scope inside it first."""
    if has_errors:
        print("Filling only error fields... ")
        input_fields = [f for f in input_fields if f.get('hasError', False)]
    for input_field in input_fields:
        if input_field['type'] == 'text':
            enter_text_field(page, input_field)
        elif input_field['type'] in ['select', 'radio']:
            select_option(page, input_field)
        elif input_field['type'] == 'combobox':
            fill_combobox(page, input_field)

def enter_text_field(page, input_field):
    """Enters text into a text field based on the provided input_field."""
    print("Filling text field:", input_field['label'])
    selector = input_field['selector']
    current_value = input_field['value']
    error = input_field.get('error', None)
    if error and not current_value:
        print(f"Field has error '{error}' but no current value. Skipping...")
        return
    new_value = get_text_answer(input_field['label'], error)
    if new_value and new_value != current_value:
        if current_value:
            page.fill(selector, '')
            page.wait_for_timeout(200)
        page.type(selector, new_value, delay=10)
        page.wait_for_timeout(timeout_1s)

def select_option(page, field_info):
    """Generically selects an option for dropdown or radio group based on the provided field_info."""
    print("Selecting option for field:", field_info['label'])
    selector = field_info['selector']
    options = field_info.get('options', [])
    label = field_info.get('label', '')
    current_value = field_info['value']
    temp_options = [opt['label'] for opt in options if opt['label'].lower() != 'select an option']
    answer = get_select_answer(label, temp_options)

    if current_value != answer:
        selected_option = next((opt for opt in options if opt['label'].strip().lower() == answer.strip().lower()), options[0])
        print(f"Selecting option '{selected_option['label']}' for field '{label}'")
        select_control(page, selected_option['selector'], selector, selected_option.get('value'))
        page.wait_for_timeout(timeout_1s)
        
def select_control(page, option_selector, field_selector, option_value=None):
    """
    Tries to select a control by first using select_option (for dropdowns), then check (for radios/checkboxes), then click input, then click label.
    """
    if option_value is not None:
        try:
            page.select_option(field_selector, option_value, timeout=timeout_2s)
            print(f"Select option used for {field_selector} with value {option_value}")
            return
        except Exception as e:
            print(f"Select option failed for {field_selector}: {e}")
    # Try check (for radio/checkbox)
    try:
        page.check(option_selector, timeout=timeout_2s)
        print(f"Checked selector: {option_selector}")
        return
    except Exception as e:
        print(f"Check failed for {option_selector}: {e}")
    # Try clicking the input
    try:
        page.click(option_selector, timeout=timeout_2s)
        print(f"Clicked selector: {option_selector}")
        return
    except Exception as e:
        print(f"Click failed for {option_selector}: {e}")
    # Try clicking the label associated with the input
    try:
        label_selector = f'label[for="{option_selector.lstrip("#")}"]'
        page.click(label_selector, timeout=timeout_2s)
        print(f"Clicked label selector: {label_selector}")
        return
    except Exception as e:
        print(f"Click label failed for {option_selector}: {e}")

def fill_combobox(page, field_info):
    """Fills out a combobox (autocomplete) field based on the provided field_info."""
    print("Filling combobox field:", field_info['label'])
    selector = field_info['selector']
    label = field_info.get('label', '')
    current_value = field_info.get('value', '')
    new_value = get_text_answer(label)

    if current_value != new_value:
        try:
            page.fill(selector, '')
            page.type(selector, new_value, delay=50)
            page.wait_for_timeout(timeout_2s)
            option_query = '[role="option"]' #, .basic-typeahead__selectable
            page.wait_for_selector(option_query, timeout=timeout_5s)
            candidates = page.query_selector_all(option_query)
            candidates[0].click(timeout=timeout_2s)
            page.wait_for_timeout(1000)
        except Exception as e:
            print(f"Failed to select combobox option for {label}: {e}")
