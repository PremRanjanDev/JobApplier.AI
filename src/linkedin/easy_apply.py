from playwright.async_api import async_playwright

async def easy_apply(page, job_title, location):
    """Performs the Easy Apply process for a job on LinkedIn."""
    print(f"Searching for jobs: {job_title} in {location}")
    await page.goto("https://www.linkedin.com/jobs/")
    await page.fill('input[aria-label="Search by title, skill, or company"]', job_title)
    await page.fill('input[aria-label="Location"]', location)
    await page.click('button[aria-label="Search"]')
    
    print("Waiting for job listings to load...")
    await page.wait_for_selector('.job-card-container--clickable')

    # Click on the first job listing
    print("Clicking on the first job listing...")
    await page.click('.job-card-container--clickable')

    # Wait for the Easy Apply button to be visible
    print("Waiting for Easy Apply button...")
    await page.wait_for_selector('button[aria-label="Easy Apply"]')
    
    # Click the Easy Apply button
    print("Clicking Easy Apply...")
    await page.click('button[aria-label="Easy Apply"]')

    # Wait for the application form to load
    print("Waiting for application form to load...")
    await page.wait_for_selector('.artdeco-modal__content')

    # Submit the application
    print("Submitting application...")
    await page.click('button[aria-label="Submit application"]')
    
    print("Application submitted successfully.")

