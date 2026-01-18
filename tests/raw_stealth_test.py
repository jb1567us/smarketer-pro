import asyncio
import os
import sys

# Hardcoded absolute path for certainty
SRC_PATH = r"d:\sandbox\smarketer-pro\src"
sys.path.insert(0, SRC_PATH)

from playwright.async_api import async_playwright
from playwright_stealth import Stealth

log_file = os.path.join(os.path.dirname(__file__), 'raw_stealth_log.txt')

def log(msg):
    with open(log_file, 'a') as f:
        f.write(msg + "\n")

if os.path.exists(log_file):
    os.remove(log_file)

async def main():
    log("Starting raw test...")
    async with async_playwright() as p:
        log("Playwright started.")
        browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        log("Browser launched.")
        page = await browser.new_page()
        log("Page created.")
        
        await Stealth().apply_stealth_async(page)
        log("Stealth applied.")
        
        wd = await page.evaluate("navigator.webdriver")
        log(f"navigator.webdriver: {wd}")
        
        await browser.close()
        log("Browser closed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        log(f"Error: {e}")
