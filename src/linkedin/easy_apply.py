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
        job_info = await read_job_info_by_ai(job_card_element_html)
        print("AI returned the following job details:")
        print(f"job_info: {job_info}")
        # Add additional info like datetime and append to the JSON file
        job_info["processed_at"] = datetime.now().isoformat()
        json_file.append(job_info)

        print(f"Processing job: {job_info.get('title', 'N/A')} at {job_info.get('company', 'N/A')} in {job_info.get('location', 'N/A')}")
        applied = await apply_job(page, job)
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

async def fetch_job_list(page, job_title, location):
    """Fetches job listings from LinkedIn based on job title and location."""
    print(f"Searching for jobs: {job_title} in {location}")
    await page.goto(f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}&f_AL=true")
    
    # Wait to finish loading the job listings
    await page.wait_for_selector('.job-card-container--clickable', timeout=wait_for_control)

    # Read job list
    return await page.query_selector_all('.job-card-container--clickable')

async def apply_job(page, job):
    """Applies to a job using the Easy Apply button."""
    try:
        # Click on the job listing
        await job.click(timeout=wait_for_control)

        # Read the job title
        await page.wait_for_selector('.topcard__title', timeout=wait_for_control)
        job_title = await page.text_content('.topcard__title')
        print(f"Applying to job: {job_title}")

        # Wait for the Easy Apply button to be available
        await page.wait_for_selector('button[aria-label^="Easy Apply"]', state='visible', timeout=wait_for_control)
        # Click the Easy Apply button
        await page.click('button[aria-label^="Easy Apply"]', timeout=wait_for_control)

        # Extract the DOM of the Easy Apply modal
        print("Extracting application form DOM...")
        modal_html = await page.eval_on_selector('.artdeco-modal__content', 'el => el.outerHTML')

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
