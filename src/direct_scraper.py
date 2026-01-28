import asyncio
import random
import csv
import argparse
import sys
import os
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from scrapers.serp_logic import extract_serp_results

# Human-like delays
MIN_TYPING_DELAY = 100  # ms
MAX_TYPING_DELAY = 300  # ms
MIN_PAGE_DELAY = 2000   # ms
MAX_PAGE_DELAY = 5000   # ms

async def human_type(page, selector, text):
    """Types text into a selector with random delays between keystrokes."""
    await page.focus(selector)
    for char in text:
        await page.keyboard.type(char, delay=random.randint(MIN_TYPING_DELAY, MAX_TYPING_DELAY))

# Engine Configuration
SEARCH_CONFIG = {
    'google': {
        'url': 'https://www.google.com',
        'consent_text': 'Before you continue to Google',
        'input_selector': 'textarea[name="q"], input[name="q"]',
        'result_selector': 'div.g', 
        'link_selector': 'a:has(h3)', # Primary strategy
        'next_selector': 'a#pnnext'
    },
    'ddg': {
        'url': 'https://duckduckgo.com',
        'consent_text': '', # DDG usually has no invasive modal
        'input_selector': '#searchbox_input', # Home page input
        'input_selector_results': '#search_form_input', # Results page input
        'result_selector': 'article',
        'link_selector': 'h2 a', # DDG titles are in h2 > a
        'next_selector': 'a#more-results' # DDG uses infinite scroll or specific buttons
    }
}

async def run_search(query, num_pages=1, headless=False, engine='google'):
    print(f"🚀 Starting Direct Search for: '{query}'")
    print(f"🌍 Engine: {engine.upper()}")
    print(f"👀 Headless Mode: {headless}")
    
    cfg = SEARCH_CONFIG.get(engine, SEARCH_CONFIG['google'])
    results = []
    
    async with async_playwright() as p:
        # Launch browser with arguments to look like a real user
        user_data_dir = os.path.join(os.getcwd(), 'chrome_profile')
        browser = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=headless,
            channel="chrome",  # Use actual Chrome if installed
            ignore_default_args=["--enable-automation"],
            args=[
                '--disable-blink-features=AutomationControlled',
                '--start-maximized',
                '--disable-infobars',
                '--window-position=0,0',
                '--ignore-certificate-errors',
                '--ignore-certificate-errors-spki-list',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
            ],
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            viewport=None, # Let window manager handle it
            locale='en-US'
        )
        
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        # [Added] Apply Stealth to masking bot signals 
        await Stealth().apply_stealth_async(page)
        
        try:
            # 1. Navigation
            print(f"🌐 Navigating to {cfg['url']}...")
            await page.goto(cfg['url'], wait_until="domcontentloaded")
            
            # [Added] Handle Cookie Consent Overlay (Google Only mostly)
            if engine == 'google':
                try:
                    # Try finding 'Reject all' or 'Accept all' buttons
                    if await page.get_by_text(cfg['consent_text']).count() > 0:
                        print("🍪 Handling Cookie Consent...")
                        reject_btn = page.get_by_role("button", name="Reject all")
                        accept_btn = page.get_by_role("button", name="Accept all") # Fallback
                        
                        if await reject_btn.count() > 0:
                            await reject_btn.click()
                        elif await accept_btn.count() > 0:
                            await accept_btn.click()
                        
                        await page.wait_for_load_state("networkidle")
                except Exception as e:
                    print(f"⚠️ Cookie handler warning: {e}")

            # [Added] Check for Bot Detection / CAPTCHA
            title = await page.title()
            content = await page.content()
            if "Sorry" in title or "robot" in content or "unusual traffic" in content:
                print("\n⚠️  DETECTION TRIGGERED ⚠️")
                print("The browser is visible. Please solve the CAPTCHA manually.")
                print("🛑 IMPORTANT: DO NOT CLOSE THE BROWSER WINDOW! Just solve the puzzle.")
                print("Once solved and you see the search bar, press ENTER in this terminal to continue...")
                input("Press Enter to continue...")

            # 2. Typing Query
            print(f"⌨️  Typing query: '{query}'")
            
            if page.is_closed():
                print("❌ Error: Browser window was closed. Cannot continue.")
                return results

            # Handle selector differences
            input_sel = cfg['input_selector']
            
            # Wait for input
            try:
                await page.wait_for_selector(input_sel, timeout=5000)
            except Exception as e:
                if page.is_closed():
                    print("❌ Error: Browser window was closed.")
                    return results
                    
                if engine == 'ddg':
                     input_sel = cfg['input_selector_results'] # Fallback for DDG results page
            
            await human_type(page, input_sel, query)
            await page.keyboard.press("Enter")
            
            # Process Pages
            for i in range(num_pages):
                print(f"📄 Processing Page {i+1}...")
                await page.wait_for_load_state("networkidle")
                
                # Random delay to read the page
                await asyncio.sleep(random.randint(MIN_PAGE_DELAY, MAX_PAGE_DELAY) / 1000)
                
                # Extract Results
                # REFACTOR: USE PURE LOGIC
                html_content = await page.content()
                page_results = extract_serp_results(html_content, engine=engine)
                
                results_count_on_page = 0
                for r in page_results:
                    # Avoid duplicates in this global mission list
                    if not any(gr['url'] == r['url'] for gr in results):
                        results.append(r)
                        results_count_on_page += 1
                        print(f"  found: {r['title'][:30]}... ({r['url'][:40]}...)")
                
                if results_count_on_page == 0:
                     print("⚠️  ZERO valid results after filtering.")
                     # Debug dump logic...
                     timestamp = f"debug_{engine}_0_results"
                     await page.screenshot(path=f"{timestamp}.png")
                     with open(f"{timestamp}.html", "w", encoding="utf-8") as f:
                        f.write(await page.content())
                     print(f"  -> Saved debug artifacts to {os.getcwd()}")
                
                # Next Page
                if i < num_pages - 1:
                    print("➡️  Moving to next page...")
                    if engine == 'ddg':
                        # DDG often uses infinite scroll, but let's try pressing "More Results" button if exists
                        more_btn = page.locator('button#more-results')
                        if await more_btn.is_visible():
                            await more_btn.click()
                        else:
                            # Scroll down
                            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            await asyncio.sleep(2)
                    else:
                        # Google
                        next_button = page.locator('a#pnnext') # Standard ID
                        if await next_button.is_visible():
                            await next_button.click()
                        else:
                            print("🚫 No 'Next' button found. Stopping.")
                            break
        
        except Exception as e:
            print(f"❌ Error: {e}")
            await browser.close()
            return results

        await browser.close()
        
    return results

def save_csv(results, filename="direct_results.csv"):
    if not results:
        print("⚠️  No results to save.")
        return
        
    keys = results[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(results)
    print(f"💾 Saved {len(results)} results to {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Direct Google Search Scraper")
    parser.add_argument("query", help="Search query (e.g. 'site:instagram.com fitness')")
    parser.add_argument("--pages", type=int, default=1, help="Number of pages to scrape")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--engine", default="google", choices=["google", "ddg"], help="Search Engine to use (google/ddg)")
    
    args = parser.parse_args()
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    data = asyncio.run(run_search(args.query, args.pages, args.headless, engine=args.engine))
    save_csv(data)
