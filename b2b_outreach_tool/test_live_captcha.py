
import asyncio
import sys
import os

# Add src to sys.path to resolve imports in bridge
sys.path.append(os.path.join(os.getcwd(), "src"))

from playwright.async_api import async_playwright
from seo_bridge import PlaywrightBaseHandler
from utils.captcha_solver import CaptchaSolver

async def run_live_test():
    print("🚀 Starting Live Local Whisper Test...")
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True) # Tool works better in headless or it might hang
        context = await browser.new_context()
        page = await context.new_page()
        
        # Configure local-whisper
        page.captcha_solver = CaptchaSolver("local-whisper", "LOCAL_USE")
        
        print("🔗 Navigating to reCAPTCHA Demo page...")
        await page.goto("https://www.google.com/recaptcha/api2/demo")
        
        handler = PlaywrightBaseHandler()
        
        print("🤖 Attempting to solve captcha via Local Whisper...")
        success = await handler.solve_page_captcha(page)
        
        if success:
            print("✅ CAPTCHA SOLVED SUCCESSFULLY!")
            # Take a screenshot to show the result
            await page.screenshot(path="captcha_solved_result.png")
            print(f"📸 Screenshot saved to captcha_solved_result.png")
        else:
            print("❌ Failed to solve captcha.")
            await page.screenshot(path="captcha_failed_result.png")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_live_test())
