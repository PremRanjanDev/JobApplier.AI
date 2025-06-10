import asyncio
from playwright.async_api import async_playwright
import os
import pathlib

LINKEDIN_STATE_FILE = "user_data/linkedin_state.json"

async def login(p, save_state=False):
    """Logs in to LinkedIn if needed and returns the browser and page objects.
    Optionally saves the browser state for future sessions."""
    if save_state:
        pathlib.Path(os.path.dirname(LINKEDIN_STATE_FILE)).mkdir(parents=True, exist_ok=True)
    if os.path.exists(LINKEDIN_STATE_FILE):
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=LINKEDIN_STATE_FILE)
        page = await context.new_page()
        print("Navigating to LinkedIn feed using saved state...")
        await page.goto("https://www.linkedin.com/feed/")
        return browser, page
    else:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        print("Navigating to LinkedIn login page...")
        await page.goto("https://www.linkedin.com/login")
        # Manual login required on first run.
        await page.wait_for_url("https://www.linkedin.com/feed/")
        print("Login successful.")
        if save_state:
            print("Saving state...")
            await context.storage_state(path=LINKEDIN_STATE_FILE)
            print(f"Login state saved to {LINKEDIN_STATE_FILE}")
        # Do not close the browser here; return it for continued use
        return browser, page

async def main():
    async with async_playwright() as p:
        browser, page = await login(p, save_state=True)
        # Keep browser open for manual inspection or further automation
        print("Browser and page are ready for further actions.")
        await page.wait_for_timeout(10000)  # Keep open for 10 seconds as an example
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
