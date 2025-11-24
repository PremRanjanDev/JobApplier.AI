import json


def extract_job_details(element):
    """
    Extracts job details from the job detail section.
    Extract details as, jobTitle, companyName, location, and description
    """
    return element.evaluate('''(element) => {
    
            // Get job title
            let jobTitle = '';
            const titleElem = element.querySelector('div[class*="job-title"]');
            if (titleElem) {
                jobTitle = titleElem.textContent.trim();
            }
            
            // Get job title
            let companyName = '';
            const companyElem = element.querySelector('div[class*="company-name"]');
            if (companyElem) {
                companyName = companyElem.textContent.trim();
            }
            
            // Get job description let jobDescription = ''; 
            const jobDescriptionElem = element.querySelector('div[class*="jobs-description"], div[class*="job-description"]'); 
            if (jobDescriptionElem) { 
                jobDescription = jobDescriptionElem.textContent.replace(/\\s{2,}/g, ' \\n').trim(); 
            }
    
            return { 
                title: jobTitle,
                company: companyName,
                description: jobDescription
            };
        }''')


def extract_form_info(element):
    """Extracts form metadata (id, header, progress) from the Easy Apply modal.
    
    Args:
        element: The modal element to extract info from
        
    Returns:
        dict: Contains id, header, and progress information
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

        return { 
            id: modal.id, 
            header: headerText, 
            progress: progress
        };
    }''')


def extract_form_fields(element):
    """Extracts input fields from the Easy Apply modal.

    Args:
        element: The modal element to extract fields from
        
    Returns:
        Array: Fields
    """
    return element.evaluate('''(modal) => {

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
        const formElements = modal.querySelectorAll('input, select, fieldset, textarea');
    
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
            else if (element.matches('input[type="text"]:not([role="combobox"]), input[type="email"], input[type="tel"], textarea')) {
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
            else if (element.matches('fieldset[data-test-form-builder-radio-button-form-component="true"], fieldset[data-test-checkbox-form-component="true"]')) {
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
        
        return fields;
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


def extract_hiring_team(job_details_section):
    """Extract hiring team (recruiters) from a '.job-details-people-who-can-help' element.

    Args:
        job_details_section: Element for the hiring team container.

    Returns:
        list[dict]: Each recruiter:
            {
                "name": str,
                "designation": str,
                "isJobPoster": bool,
                "messageButton": {
                    "label": str,
                    "selector": str,
                    "isEnabled": bool,
                } | None
            }
    """
    recruiters = []
    if not job_details_section:
        return recruiters

    cards = job_details_section.query_selector_all('div[class*="hirer-card__hirer-information"]')
    if not cards:
        return recruiters

    for card in cards:
        try:
            name = card.query_selector(".jobs-poster__name").inner_text().strip()
            designation = card.query_selector(".linked-area .text-body-small").inner_text().strip()
            is_job_poster = "Job poster" in (card.inner_text() or "")
            msg_btn_el = card.query_selector("button span:text('Message')")
            message_button = None
            if msg_btn_el:
                label = (msg_btn_el.inner_text() or "").strip()
                btn_id = msg_btn_el.get_attribute("id")
                selector = f"button#{btn_id}" if btn_id else ".entry-point button.artdeco-button"
                is_enabled = bool(getattr(msg_btn_el, "is_enabled", lambda: True)())
                message_button = {
                    "label": label,
                    "selector": selector,
                    "isEnabled": is_enabled,
                }

            recruiters.append(
                {
                    "name": name,
                    "designation": designation,
                    "isJobPoster": is_job_poster,
                    "messageButton": message_button,
                }
            )
        except Exception as e:
            print(f"Failed to parse hiring team member: {e}")

    return recruiters


def form_state(form_info, form_fields):
    """Returns a hashable representation of the form's header and its fields/values."""
    return json.dumps({
        "id": form_info.get("id", ""),
        "header": form_info.get("header", ""),
        "progress": form_info.get("progress", ""),
        "fields": [f'{field["label"]}:{field.get("error", "")}:{field["value"]}' for field in form_fields],
    })