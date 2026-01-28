import asyncio
import os
import csv
import sys
import argparse
from typing import List, Dict

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from search_providers.direct_browser import DirectBrowser
from maps.logic import parse_list_item, parse_detail_page

class MapsParser:
    """
    Parser that visits Google Maps URLs (search results or places) and extracts business details.
    """
    def __init__(self, input_file="data/harvested_maps_links.csv", output_file="data/extracted_businesses.csv"):
        self.input_file = input_file
        self.output_file = output_file
        self.browser = DirectBrowser(headless=False) # Headless=False to avoid extensive bot detection
        self.ensure_output_dir()

    def ensure_output_dir(self):
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

    async def parse(self):
        """
        Main loop: Read input CSV -> Visit URL -> Extract Data -> Write Output CSV.
        """
        if not os.path.exists(self.input_file):
            print(f"❌ Input file not found: {self.input_file}")
            return

        print(f"🏗️ MapsParser: processing {self.input_file}...")
        
        # Load tasks
        tasks = []
        with open(self.input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            tasks = list(reader)

        processed_count = 0
        
        for row in tasks:
            url = row.get("maps_url")
            city = row.get("city")
            if not url: continue
            
            print(f"\n📍 Visiting: {url} ({city})")
            
            # Use DirectBrowser's internal playwright context
            # We need to expose a method in DirectBrowser to just "visit and let me scrape"
            # acts like get_page_content but with a persistent context.
            # Actually, let's use a new method we'll add to DirectBrowser or just use internal logic here?
            # Better to add `visit_and_extract` hook or use `get_page_content` if we updated it to use persistent context (YES WE DID in Step 190).
            
            # However, get_page_content returns HTML string. We might need the PAGE object to interact (scroll list).
            # So we should probably instantiate Playwright here or make DirectBrowser yield a page.
            
            # Let's simple-hack: Use a dedicated method in MapsParser that initializes Playwright similarly to DirectBrowser
            # Or extend DirectBrowser.
            
            # For now, I'll implement the browser logic here to have full control over selectors.
            
            # ... implementation continues below ...
            pass
            
    async def run_extraction(self):
        """
        Implementation of the browser automation.
        """
        from playwright.async_api import async_playwright
        from playwright_stealth import Stealth
        
        tasks = []
        if os.path.exists(self.input_file):
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                tasks = list(reader)
        
        async with async_playwright() as p:
            user_data_dir = os.path.join(os.getcwd(), 'chrome_profile')
            
            # Launch persistent
            browser = await p.chromium.launch_persistent_context(
                user_data_dir,
                headless=False,
                channel="chrome",
                ignore_default_args=["--enable-automation"],
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--start-maximized',
                    '--disable-infobars'
                ],
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                viewport=None
            )
            
            page = browser.pages[0] if browser.pages else await browser.new_page()
            await Stealth().apply_stealth_async(page)
            
            for row in tasks:
                url = row.get("maps_url")
                if not url: continue
                
                try:
                    await page.goto(url, wait_until="domcontentloaded")
                    await asyncio.sleep(3) # Wait for UI
                    
                    # Check for Consent
                    try:
                        if await page.get_by_text("Before you continue").count() > 0:
                            await page.get_by_role("button", name="Reject all").click()
                            await asyncio.sleep(2)
                    except: pass
                    
                    # Detect Page Type
                    # List View usually has role="feed" or aria-label="Results for..."
                    # Detail view has h1 matching the place name significantly
                    
                    # Heuristic: Look for "feed" (sidebar list)
                    # Use a very generic scrape strategy first:
                    
                    # Is it a search result list?
                    items = await page.locator('div[role="feed"] > div > div[role="article"]').all()
                    
                    if len(items) > 0:
                        print(f"  📋 Detected List View with {len(items)} items (visible). Scraping...")
                        # Scroll to load more?
                        # For V1, just take what's visible
                        
                        for item in items:
                            try:
                                print(f"    - Found Item")
                                
                                # REFACTOR: USE PURE LOGIC
                                # We need inner HTML for the parser
                                html = await item.inner_html()
                                data = parse_list_item(html)
                                
                                # Merge context data
                                data.update({
                                     "city": row.get("city"),
                                     "source_url": url,
                                     "state": self._parse_state(row.get("city")), # Add state/country if needed
                                     "country": row.get("country", "")
                                })
                                
                                self.save_business(data)
                            except Exception as e:
                                print(f"    Item parse err: {e}")
                                continue
                                
                    else:
                        # Detail View?
                        print("  Checking for Detail View...")
                        h1 = page.locator("h1")
                        if await h1.count() > 0:
                            print(f"  🏢 Detail View Detected")
                            
                            # REFACTOR: USE PURE LOGIC
                            html = await page.content()
                            data = parse_detail_page(html)
                            
                            # Add Context
                            data.update({
                                "city": self._parse_city(row.get("city")),
                                "state": self._parse_state(row.get("city")),
                                "country": row.get("country", ""),
                                "source_url": url,
                                "maps_url": page.url
                            })

                            print(f"    Parsed: {data['business_name']}")
                            self.save_business(data)
                            
                except Exception as e:
                    print(f"  ❌ Failed to parse {url}: {e}")

            await browser.close()

    def _parse_city(self, location_str):
        if not location_str: return ""
        if "," in location_str:
            return location_str.split(",")[0].strip()
        return location_str

    def _parse_state(self, location_str):
        if not location_str: return ""
        if "," in location_str:
            parts = location_str.split(",")
            if len(parts) > 1:
                return parts[1].strip()
        return ""

    def save_business(self, data):
        file_exists = os.path.exists(self.output_file)
        fieldnames = ["business_name", "website", "phone", "city", "state", "country", "maps_url", "source_url"]
        with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

if __name__ == "__main__":
    parser = MapsParser()
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(parser.run_extraction())
