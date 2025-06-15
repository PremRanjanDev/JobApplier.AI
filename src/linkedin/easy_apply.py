from ai.ai_utils import read_job_info_by_ai, read_job_form_by_ai
from utils.json_utils import JsonFile
import os
from datetime import datetime

wait_for_control = 5000 # 5 seconds timeout for waiting for controls

async def apply_jobs_easy_apply(page, keyword, location):
    """Performs the Easy Apply process for a jobs on LinkedIn."""
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

    jobs = await fetch_job_list(page, keyword, location)

    if not jobs:
        print("No job listings found. Please check the job title and location.")
        return
    print(f"Found {len(jobs)} job listings.")

    for job in jobs:
        # Parse the job element using AI and fetch details like id, title, company, location, type, etc.
        print("Processing job...")
        job_id = await job.get_attribute('data-job-id')
        print(f"Job ID: {job_id}")
        job_card_element_html = await job.inner_html()
        print("Extracting job details from HTML...")
        job_info = await read_job_info_by_ai(job_card_element_html)
        print("AI returned the following job details:")
        print(f"job_info: {job_info}")
        if "selector" in job_info and job_info["selector"]:
            try:
                await page.click(job_info["selector"], timeout=wait_for_control)
                print(f"Clicked element with selector: {job_info['selector']}")
            except Exception as e:
                print(f"Failed to click element with selector {job_info['selector']}: {e}")
        # Add additional info like datetime and append to the JSON file
        job_info["processed_at"] = datetime.now().isoformat()
        json_file.append(job_info)

        if job_info.get('applied', False):
            print("Job already applied or Easy Apply button not found. Skipping this job.")
            continue

        print(f"Processing job: {job_info.get('title', 'N/A')} at {job_info.get('company', 'N/A')} in {job_info.get('location', 'N/A')}")
        
        applied = await apply_job(page, job, job_info)
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
    #         await page.fill(selector, value)
    #     elif field_type == 'radio':
    #         # Select the first option or a preferred one
    #         if options:
    #             await page.check(options[0]['selector'])
    #     elif field_type == 'checkbox':
    #         # Check if value is True or similar logic
    #         if value:
    #             await page.check(selector)
    #     # Add more field types as needed

    # # Submit the application
    # print("Submitting application...")
    # await page.click('button[aria-label="Submit application"]', timeout=wait_for_control)
    
    # print("Application submitted successfully.")

async def fetch_job_list(page, job_title, location, page_number=1):
    """Fetches job listings from LinkedIn based on job title and location."""
    print(f"Searching for jobs: {job_title} in {location}")
    await page.goto(f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}&f_AL=true")
    
    # Click the pagination button for the current page
    if page_number > 1:
        pagination_selector = f'button[aria-label="Page {page_number}"]'
        try:
            await page.wait_for_selector(pagination_selector, timeout=wait_for_control)
            await page.click(pagination_selector, timeout=wait_for_control)
            await page.wait_for_timeout(2000)  # Wait for the page to load jobs
        except Exception as e:
            print(f"Could not click pagination button for page {page_number}: {e}")

    await page.wait_for_timeout(2000) # Wait for the page to load jobs
    jobs = await page.query_selector_all('.job-card-container--clickable')

    prev_job_len = 0
    while len(jobs) != prev_job_len:
        print(f"Found {len(jobs)} jobs, scrolling to load more...")
        prev_job_len = len(jobs)
        # Scroll the last job card into the center of the viewport for better visibility/loading
        await page.evaluate(
            '(el) => el.scrollIntoView({behavior: "smooth", block: "center"})',
            jobs[-1]
        )
        await page.wait_for_timeout(1000)  # Wait for more jobs to load
        jobs = await page.query_selector_all('.job-card-container--clickable')
    
    return jobs

async def apply_job(page, job, job_info):
    """Applies to a job using the Easy Apply button."""
    try:
        # Click on the job listing
        # job_id = await job.get_attribute('data-job-id')
        # if not job_id:
        #     print("Job element does not have a data-job-id attribute.")
        #     return False
        # Re-query the job element to ensure it is attached to the DOM
        # job_selector = f'.job-card-container--clickable[data-job-id="{job_id}"]'
        # fresh_job = await page.query_selector(job_selector)
        # if not fresh_job:
            # print(f"Could not find job element with selector: {job_selector}")
            # return False
        # Re-query the element right before clicking to avoid stale element reference
        # fresh_job = await page.query_selector(job_selector)
        # if not fresh_job:
        #     print(f"Job element became detached before clicking: {job_selector}")
        #     return False
        # await fresh_job.click(timeout=wait_for_control)

        # Wait for the job details page to load
        # Wait for the job details section and select it
        job_details_section = await page.wait_for_selector(
            'div[class*="job-details"], div[class*="jobs-details"], div[class*="job-view-layout"]',
            timeout=wait_for_control
        )
        easy_apply_button = None
        if job_details_section:
            easy_apply_button = await job_details_section.query_selector('button[aria-label^="Easy Apply"]')
        if not easy_apply_button:
            # Check if already applied by looking for the feedback message
            applied_message_elem = await page.query_selector('.artdeco-inline-feedback--success .artdeco-inline-feedback__message')
            if applied_message_elem:
                applied_message = await applied_message_elem.inner_text()
                print(f"Already applied to this job. Status: {applied_message.strip()}")
                return False
            print("Already applied or Easy Apply button not found. Skipping this job.")
            return False
        # Click the Easy Apply button
        await easy_apply_button.click()

        # Extract the DOM of the Easy Apply modal
        print("Extracting application form DOM...")
        modal_html = await page.inner_html('.artdeco-modal__content')
        if not modal_html:
            print("Could not extract the application form DOM. Skipping this job.")
            return False

        # Use the AI utility for form field extraction
        fields_info = await read_job_form_by_ai(modal_html)
        print("AI returned the following fields info:")
        print(fields_info)

        # Wait for the application form to load
        await page.wait_for_selector('.artdeco-modal__content', timeout=wait_for_control)

        # Fill out the application form (this part will be handled by AI fields_info)
        return True  # Indicate success
    except Exception as e:
        print(f"Error applying to job {getattr(job, 'title', 'Unknown')}: {e}")
        return False  # Indicate failure
