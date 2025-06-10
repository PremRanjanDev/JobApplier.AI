import asyncio
from playwright.async_api import async_playwright
import os
import pathlib
from login import login
from easy_apply import easy_apply

async def main():
    async with async_playwright() as p:
        # Initialize the login process
        print("Starting LinkedIn login process...")
        browser, page = await login(p, save_login=True)
        print("Logged in to LinkedIn successfully.")

        # Perform the easy apply process
        print("Starting the Easy Apply process...")
        await easy_apply(page, "Java developer", "Sinapore")
  
        print("Easy apply finished. Keeping browser open (10 sec) for inspection.")
        await page.wait_for_timeout(10000)  # Keep open for 10 seconds as an example
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
