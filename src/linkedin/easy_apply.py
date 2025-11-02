from ai.ai_helper import read_job_info_by_ai, read_job_form_by_ai
from ai.openai_provider import get_text_answer, get_select_answer
from utils.json_utils import JsonFile
import os
from datetime import datetime
import json

timeout_5s = 5000 # 5 seconds timeout for waiting for controls
timeout_2s = 2000 # 2 seconds timeout for waiting for clicks

def apply_jobs_easy_apply(page, keyword, location):
    """Performs the Easy Apply process for a jobs on LinkedIn."""
    print("Starting the Easy Apply process...")
    # Create an output file to log the job applications
    output_dir = "output/linkedin"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"easy_apply_{current_time}.json")
    json_file = JsonFile(output_file)
    apply_info = {
        "record":"Apply info",
        "keyword": keyword,
        "location": location,
        "timestamp": datetime.now().isoformat()
    }
    json_file.append(apply_info)

    jobs = fetch_job_list(page, keyword, location)

    if not jobs:
        print("No job listings found. Please check the job title and location.")
        return
    print(f"Found {len(jobs)} job listings.")

    for job in jobs:
        # Parse the job element using AI and fetch details like id, title, company, location, type, etc.
        print("Processing job...")
        job_id = job.get_attribute('data-job-id')
        print(f"Job ID: {job_id}")
        # job_card_element_html = job.inner_html()
        # print("Extracting job info from HTML...")
        # job_info = read_job_info_by_ai(job_card_element_html)
        # print("AI returned the following job details:")
        # print(f"job_info: {job_info}")
        # if "selector" in job_info and job_info["selector"]:
        #     try:
        #         page.click(job_info["selector"], timeout=wait_for_control)
        #         print(f"Clicked element with selector: {job_info['selector']}")
        #     except Exception as e:
        #         print(f"Failed to click element with selector {job_info['selector']}: {e}")
        # # Add additional info like datetime and append to the JSON file
        # job_info["record"] = "Job Info"
        # job_info["processed_at"] = datetime.now().isoformat()
        # json_file.append(job_info)
# 
        # if job_info.get('applied', False):
        #     print("Job already applied or Easy Apply button not found. Skipping this job.")
        #     continue
        # 
        # print(f"Processing job: {job_info.get('title', 'N/A')} at {job_info.get('company', 'N/A')} in {job_info.get('location', 'N/A')}")
        
        applied = apply_job(page, job)
        if applied:
            print("Successfully applied.")
        else:
            print("Failed to apply.")

    # Example: Fill the form based on OpenAI's response
    # for field in fields_info:
    #     selector = field.get('selector')
    #     field_type = field.get('type')
    #     label = field.get('label')
    #     options = field.get('options', [])
    #     value = field.get('value', '')  # You may want to generate or fetch this value
    #     print(f"Filling {label} ({field_type}) with value: {value}")
    #     if field_type == 'text':
    #         page.fill(selector, value)
    #     elif field_type == 'radio':
    #         # Select the first option or a preferred one
    #         if options:
    #             page.check(options[0]['selector'])
    #     elif field_type == 'checkbox':
    #         # Check if value is True or similar logic
    #         if value:
    #             page.check(selector)
    #     # Add more field types as needed

    # # Submit the application
    # print("Submitting application...")
    # page.click('button[aria-label="Submit application"]', timeout=wait_for_control)
    
    # print("Application submitted successfully.")

def fetch_job_list(page, job_title, location, page_number=1):
    """Fetches job listings from LinkedIn based on job title and location."""
    print(f"Searching for jobs: {job_title} in {location}")
    page.goto(f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}&f_AL=true")
    
    print("Current page number:", page_number)
    if page_number > 1:
        pagination_selector = f'button[aria-label="Page {page_number}"]'
        try:
            page.wait_for_selector(pagination_selector, timeout=timeout_5s)
            page.click(pagination_selector, timeout=timeout_2s)
            page.wait_for_timeout(2000)  # Wait for the page to load jobs
        except Exception as e:
            print(f"Could not click pagination button for page {page_number}: {e}")

    page.wait_for_timeout(2000) # Wait for the page to load jobs
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
        page.wait_for_timeout(1000)  # Wait for more jobs to load
        jobs = page.query_selector_all('.job-card-container--clickable')
    
    return jobs

def extract_form_fields(element):
    """Extracts input fields from the Easy Apply modal.
    
    Args:
        element: The modal element to extract fields from
    """
    return element.evaluate('''(modal) => {

        // Get header text
        let headerText = '';
        const headerElem = modal.querySelector('.artdeco-modal__header h2');
        if (headerElem) {
            headerText = headerElem.textContent.trim();
        }

        // Try to read application progress
        let progress = null;
        const progressElem = modal.querySelector('span[role="note"][aria-label*="progress"], span[aria-label*="progress"], span[role="note"]');
        if (progressElem) {
            // Return the visible inner text (e.g. "25%")
            progress = (progressElem.textContent || '').trim();
        }

        const getFieldError = (element) => {
            const errorId = element.getAttribute('aria-describedby');
            if (errorId) {
                const errorEl = modal.querySelector(`#${errorId} .artdeco-inline-feedback--error .artdeco-inline-feedback__message`);
                if (errorEl) {
                    return errorEl.textContent.trim();
                }
            }
            
            const container = element.closest('.fb-dash-form-element');
            if (container) {
                const errorEl = container.querySelector('.artdeco-inline-feedback--error .artdeco-inline-feedback__message');
                if (errorEl) {
                    return errorEl.textContent.trim();
                }
            }
            return null;
        };

        const fields = [];
        const formElements = modal.querySelectorAll('input, select, fieldset');
        
        formElements.forEach(element => {
            if (element.type === 'hidden' || !element.offsetParent) {
                return;
            }

            let fieldData = null;

            // Handle combobox inputs
            if (element.matches('input[role="combobox"]')) {
                const listId = element.getAttribute('aria-controls') || element.getAttribute('aria-owns') || '';
                let options = [];
                if (listId) {
                    const listEl = modal.querySelector('#' + listId) || document.querySelector('#' + listId);
                    if (listEl) {
                        options = Array.from(listEl.querySelectorAll('[role="option"], .basic-typeahead__selectable')).map((opt, idx) => {
                            const textElem = opt.querySelector('.search-typeahead-v2__hit-text') || opt.querySelector('span') || opt;
                            const txt = (textElem && textElem.textContent) ? textElem.textContent.trim() : (opt.textContent || '').trim();
                            return {
                                label: txt,
                                selector: opt.id ? ('#' + opt.id) : null
                            };
                        });
                    }
                }
                fieldData = {
                    type: 'combobox',
                    label: element.labels?.[0]?.querySelector('span[aria-hidden="true"]')?.textContent.trim() || element.labels?.[0]?.innerText.trim() || '',
                    selector: '#' + element.id,
                    value: element.value || '',
                    listbox: listId,
                    options: options
                };
            }
            // Text inputs (exclude comboboxes handled above)
            else if (element.matches('input[type="text"]:not([role="combobox"]), input[type="email"], input[type="tel"]')) {
                fieldData = {
                    type: 'text',
                    label: element.labels?.[0]?.querySelector('span[aria-hidden="true"]')?.textContent.trim() || element.labels?.[0]?.innerText.trim() || '',
                    selector: '#' + element.id,
                    value: element.value || ''
                };
            }
            // Select dropdowns
            else if (element.matches('select')) {
                const options = Array.from(element.options).map((opt, idx) => ({
                    label: opt.textContent.trim(),
                    selector: '#' + element.id + ' > option:nth-child(' + (idx + 1) + ')',
                    value: opt.value,
                    isSelected: opt.selected
                }));
                const topOptions = options.length > 10 ? options.slice(0, 10) : options;
                fieldData = {
                    type: 'select',
                    label: element.labels?.[0]?.querySelector('span[aria-hidden="true"]')?.textContent.trim() || element.labels?.[0]?.innerText.trim() || '',
                    selector: '#' + element.id,
                    value: element.value,
                    options: topOptions
                };
            }
            // Radio groups
            else if (element.matches('fieldset[data-test-form-builder-radio-button-form-component="true"]')) {
                let label = '';
                const legend = element.querySelector('legend');
                if (legend) {
                    const spanLabel = legend.querySelector('span[aria-hidden="true"]');
                    label = spanLabel ? spanLabel.textContent.trim() : legend.textContent.trim();
                }

                const radioInputs = element.querySelectorAll('input[type="radio"]');
                const options = Array.from(radioInputs).map((input, idx) => {
                    let optionLabel = '';
                    const labelElem = element.querySelector(`label[for="${input.id}"]`);
                    if (labelElem) {
                        optionLabel = labelElem.textContent.trim();
                    } else if (input.nextElementSibling && input.nextElementSibling.tagName === 'LABEL') {
                        optionLabel = input.nextElementSibling.textContent.trim();
                    } else {
                        optionLabel = input.value || `Option ${idx + 1}`;
                    }
                    return {
                        label: optionLabel,
                        selector: '#' + input.id,
                        value: input.value,
                        isSelected: input.checked
                    };
                });

                const selected = options.find(opt => opt.isSelected);
                fieldData = {
                    type: 'radio',
                    label: label,
                    selector: '#' + element.id,
                    value: selected ? selected.value : '',
                    options: options
                };
            }

            if (fieldData) {
                const errorMessage = getFieldError(element);
                if (errorMessage) {
                    fieldData.error = errorMessage;
                    fieldData.hasError = true;
                }
                fields.push(fieldData);
            }
        });

        return { 
            id: modal.id, 
            header: headerText, 
            progress: progress, 
            fields: fields,
            hasErrors: fields.some(f => f.hasError),
            totalErrors: fields.filter(_ => _.hasError).length
        };
    }''')

def extract_step_controls(element):
    """Extracts all step control buttons as (nextButton, backButton, etc.) from the given Easy Apply modal element."""
    return element.evaluate('''(modal) => {
        const controls = {
            nextButton: null,
            backButton: null,
            closeButton: null,
            saveButton: null,
            discardButton: null,
            otherButtons: []
        };

        modal.querySelectorAll('button').forEach(button => {
            const label = button.innerText.trim();
            const selector = button.id ? ('#' + button.id) : null;
            const ariaLabel = button.getAttribute('aria-label')?.toLowerCase() || '';
            const className = button.className?.toLowerCase() || '';

            if (
                label.toLowerCase().includes('next') ||
                label.toLowerCase().includes('review') ||
                label.toLowerCase().includes('submit') ||
                label.toLowerCase().includes('continue') ||
                label.toLowerCase().includes('done')
            ) {
                controls.nextButton = { label, selector };
            } else if (
                label.toLowerCase().includes('back') ||
                label.toLowerCase().includes('previous')
            ) {
                controls.backButton = { label, selector };
            } else if (label.toLowerCase().includes('save')) {
                controls.saveButton = { label, selector };
            } else if (label.toLowerCase().includes('discard')) {
                controls.discardButton = { label, selector };
            } else if (
                label.toLowerCase().includes('close') ||
                label.toLowerCase().includes('dismiss') ||
                label.toLowerCase().includes('cancel') ||
                ariaLabel.includes('close') ||
                ariaLabel.includes('dismiss') ||
                ariaLabel.includes('cancel') ||
                className.includes('dismiss') ||
                className.includes('close')
            ) {
                controls.closeButton = { label: ariaLabel || label, selector };
            } else {
                controls.otherButtons.push({ label, selector });
            }
        });

        return controls;
    }''')

def form_state(form_info):
    """Returns a hashable representation of the form's header and its fields/values."""
    return json.dumps({
        "id": form_info.get("id", ""),
        "header": form_info.get("header", ""),
        "progress": form_info.get("progress", ""),
        "fields": [f'{field["label"]}:{field.get("error", "")}:{field["value"]}' for field in form_info.get("fields", [])],
    })

def apply_job(page, job):
    """Applies to a job using the Easy Apply button, handling multi-step forms."""
    print("Applying to job...")
    try:
        page.wait_for_timeout(timeout_2s)
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
        fresh_job = page.query_selector(job_selector)
        if not fresh_job:
            print(f"Job element became detached before clicking: {job_selector}")
            return False
        fresh_job.click(timeout=timeout_5s)

        print("Waiting for job details to load...")
        job_details_section = page.wait_for_selector(
            'div[class*="job-details"], div[class*="jobs-details"], div[class*="job-view-layout"]',
            timeout=timeout_5s
        )
        easy_apply_button = None
        if job_details_section:
            easy_apply_button = job_details_section.query_selector('button[aria-label^="Easy Apply"]')
        if not easy_apply_button:
            applied_message_elem = page.query_selector('.artdeco-inline-feedback--success .artdeco-inline-feedback__message')
            if applied_message_elem:
                applied_message = applied_message_elem.inner_text()
                print(f"Already applied to this job. Status: {applied_message.strip()}")
                return False, "Already applied"
            print("Already applied or Easy Apply button not found. Skipping this job.")
            return False, "Already applied"
        easy_apply_button.click()

        # Multi-step form loop
        previous_state = None
        while True:
            print("Extracting application form DOM...")
            try:
                application_form = page.wait_for_selector(
                    '[class*="easy-apply-modal"], [class^="artdeco-modal"]',
                    timeout=timeout_5s
                )
            except Exception:
                # Modal disappeared before we could read it — assume finished
                print("Application modal not found (may have been closed). Assuming finished.")
                return True, "Application finished"

            if not application_form:
                print("Could not find the application form modal. Skipping this job.")
                return False, "Application form not found"

            form_info = extract_form_fields(application_form)
            input_fields = form_info['fields']
            step_controls = extract_step_controls(application_form)
            current_state = form_state(form_info)
            has_errors = form_info.get('hasErrors', False)
            if previous_state == current_state:
                print("Form state did not change after filling. Dismissing application.")
                dismiss_job_apply(page, step_controls)
                return False, "Form stuck, cannot proceed"
            
            fill_all_fields(page, input_fields, has_errors)
            previous_state = current_state

            # Try to click next, submit or done, or dismiss if stuck
            if step_controls and step_controls['nextButton']:
                page.wait_for_timeout(timeout_2s)
                print("Clicking Next button... ", step_controls['nextButton']['label'])
                next_button = page.query_selector(step_controls['nextButton']['selector'])
                if next_button:
                    page.evaluate('''(el) => {
                        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }''', next_button)
                    page.wait_for_timeout(1000)
                    page.click(step_controls['nextButton']['selector'], timeout=timeout_2s)
                    page.wait_for_timeout(timeout_2s)
            else:
                print("No Next button found, dismissing application.")
                dismiss_job_apply(page, step_controls)
                return False, "No next button"
    except Exception as e:
        print(f"Error applying to job {getattr(job, 'title', 'Unknown')}: {e}")
        dismiss_job_apply(page, None)
        return

def dismiss_job_apply(page, step_controls=None):
    print("Could not find next button in step controls.")
    if not step_controls:
        step_controls = extract_step_controls(page)
    
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
    if current_value != new_value:
        page.fill(selector, '')
        page.type(selector, new_value, delay=50)
        page.wait_for_timeout(1000)

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
        page.wait_for_timeout(1000)
        
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
