from playwright.sync_api import sync_playwright
from linkedin.login import login
from linkedin.easy_apply import apply_jobs_easy_apply

def main():
    with sync_playwright() as p:
        # Initialize the login process
        print("Starting LinkedIn login process...")
        browser, page = login(p, save_login=True)
        print("Logged in to LinkedIn successfully.")

        # Perform the easy apply process
        print("Starting the Easy Apply process...")
        apply_jobs_easy_apply(page, "Java developer", "Singapore")
  
        print("Easy apply finished. Keeping browser open (10 sec) for inspection.")
        page.wait_for_timeout(10000)  # Keep open for 10 seconds as an example
        browser.close()

if __name__ == "__main__":
    main()
