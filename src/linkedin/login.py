import asyncio
from playwright.async_api import async_playwright
import os
import pathlib

LINKEDIN_STATE_FILE = "user_data/linkedin_state.json"

async def _login_with_saved_state(p):
    print("Login in using saved LinkedIn state...")
    browser = await p.chromium.launch(
        headless=False,
        args=["--start-maximized"]
    )
    context = await browser.new_context(storage_state=LINKEDIN_STATE_FILE, viewport=None)
    page = await context.new_page()
    print("Navigating to LinkedIn feed using saved state...")
    await page.goto("https://www.linkedin.com/feed/")
    return browser, page

async def _login_manually(p, save_login=False):
    print("Login in manually...")
    browser = await p.chromium.launch(
        headless=False,
        args=["--start-maximized"]
    )
    context = await browser.new_context(viewport=None)
    page = await context.new_page()
    print("Navigating to LinkedIn login page...")
    await page.goto("https://www.linkedin.com/login")
    # Manual login required on first run.
    await page.wait_for_url("https://www.linkedin.com/feed/")
    print("Login successful.")
    if save_login:
        print("Saving state...")
        await context.storage_state(path=LINKEDIN_STATE_FILE)
        print(f"Login state saved to {LINKEDIN_STATE_FILE}")
    return browser, page

async def login(p, save_login=False):
    """Logs in to LinkedIn if needed and returns the browser and page objects.
    Optionally saves the browser state for future sessions."""
    if save_login:
        pathlib.Path(os.path.dirname(LINKEDIN_STATE_FILE)).mkdir(parents=True, exist_ok=True)
    if os.path.exists(LINKEDIN_STATE_FILE):
        return await _login_with_saved_state(p)
    else:
        return await _login_manually(p, save_login)
