import asyncio
import aiohttp
import re
import random
from urllib.parse import quote, urlparse
from bs4 import BeautifulSoup
from config import config
from scraper import search_searxng
from utils.browser_manager import BrowserManager

VALID_PLATFORMS = ["twitter", "linkedin", "tiktok", "instagram", "reddit", "youtube"]

class SocialScraper:
    """
    Unified Social Media Scraper (Filtered + Throttled).
    Combines:
    1. "X-Ray" Dorks (Search Engine) -> Used as a Filter
    2. Headless Browser (Playwright) -> High Fidelity, limited concurrency
    """
    def __init__(self):
        self.browser_manager = None
        self.browser_semaphore = asyncio.Semaphore(5) # Limit to 5 concurrent browsers

    async def _get_browser(self):
        if not self.browser_manager:
            self.browser_manager = BrowserManager(session_id="social_scraper")
            await self.browser_manager.launch(headless=True)
        return self.browser_manager.page

    async def close(self):
        if self.browser_manager:
            await self.browser_manager.close()

    async def smart_scrape(self, query_or_url, platform=None):
        """
        The Dork-First Router.
        1. Checks for existence via Search Dork.
        2. If promising, opens Browser to scrape context.
        """
        # 1. Normalize Input
        target_type = "url" if query_or_url.startswith("http") else "handle"
        
        if not platform and target_type == "url":
            platform = self._detect_platform(query_or_url)
        
        if not platform:
            return {"error": "Could not detect platform. Please specify one."}

        print(f"  [SocialScraper] Targeted: {platform} ({target_type})")

        # 2. Strategy: Filter First
        dork_results = await self._try_dork_search(query_or_url, platform)
        
        # If Dork failed to find ANY indexed pages, it's likely a dead/private profile or bad query
        # But we still might want to try browser if it's a direct URL
        should_use_browser = False
        
        if target_type == "url":
             should_use_browser = True # Always try browser for direct URLs if dork is ambiguous
        elif dork_results and len(dork_results.get("results", [])) > 0:
             should_use_browser = True # Dork found hits, so it's a real person
             # We can try to extract a URL from the dork result to visit
             # For now, if we only have a handle, we might need to construct the URL
             if target_type == "handle":
                query_or_url = self._construct_url(platform, query_or_url)

        if not should_use_browser:
             return {
                 "source": "dork_filter",
                 "status": "skipped_low_relevance",
                 "dork_data": dork_results
             }

        # 3. Strategy: Throttled Browser
        async with self.browser_semaphore:
            print(f"  [SocialScraper] Acquiring Browser Slot (Limit: 5)...")
            browser_data = await self._try_browser_scrape(query_or_url)
            
        if browser_data:
            return browser_data
            
        # Fallback to just dork data if browser failed
        if dork_results:
            return dork_results

        return {"error": "All scraping methods failed.", "platform": platform}
            
    def _detect_platform(self, url):
        u = url.lower()
        if "linkedin.com" in u: return "linkedin"
        if "twitter.com" in u or "x.com" in u: return "twitter"
        if "tiktok.com" in u: return "tiktok"
        if "instagram.com" in u: return "instagram"
        if "reddit.com" in u: return "reddit"
        if "youtube.com" in u: return "youtube"
        return None

    def _construct_url(self, platform, handle):
        handle = handle.replace("@", "")
        if platform == "twitter": return f"https://twitter.com/{handle}"
        if platform == "tiktok": return f"https://tiktok.com/@{handle}"
        if platform == "instagram": return f"https://instagram.com/{handle}"
        if platform == "linkedin": return f"https://linkedin.com/in/{handle}" # Guess
        return None

    async def _try_dork_search(self, target, platform):
        """
        Uses SearXNG with site: operators to find content.
        """
        print(f"  [SocialScraper] Attempting X-Ray Dork...")
        
        async with aiohttp.ClientSession() as session:
            
            site_map = {
                "linkedin": "site:linkedin.com/in",
                "twitter": "site:twitter.com",
                "tiktok": "site:tiktok.com/@",
                "reddit": "site:reddit.com"
            }
            
            if platform not in site_map: return None
            
            # If target is a URL, extract the uniquely identifying part for the dork
            search_term = target
            if "http" in target:
                parts = target.rstrip('/').split('/')
                search_term = parts[-1] 

            dork = f'{site_map[platform]} "{search_term}"'
            
            # [ENHANCEMENT] B2B Relevance Boost (Dynamic Context)
            # If we are looking for high-value targets, we can optional append footprints
            # e.g. for LinkedIn, prioritize "hiring" or "founder"
            if platform == "linkedin":
                dork += ' ("hiring" OR "founder" OR "owner" OR "ceo")'
            
            results = await search_searxng(dork, session, num_results=5)
            
            if results:
                 return {
                     "source": "xray_dork",
                     "results": results,
                     "note": "Indexed pages found."
                 }
        return None

    async def _try_browser_scrape(self, url):
        """
        Uses Playwright to render and dump the page.
        """
        print(f"  [SocialScraper] Attempting Headless Browser (Playwright)...")
        try:
            page = await self._get_browser()
            
            # Anti-detect measures
            await page.set_extra_http_headers({
                "Accept-Language": "en-US,en;q=0.9"
            })
            
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(2) # Initial render
            
            # Scroll for lazy load
            for _ in range(3):
                await page.mouse.wheel(0, 500)
                await asyncio.sleep(1)
            
            # Snapshot
            title = await page.title()
            content = await page.content()
            
            # Intelligent Extraction (Simplified)
            # We assume the user (Agent) will parse the raw text/HTML or we use specific selectors
            
            soup = BeautifulSoup(content, 'html.parser')
            text_dump = soup.get_text(separator='\n', strip=True)[:5000] # Cap size
            
            return {
                "source": "browser_snapshot",
                "title": title,
                "url": url,
                "raw_text_preview": text_dump,
                "html_snippet": content[:2000] # For advanced parsing if needed
            }
            
        except Exception as e:
            print(f"  [SocialScraper] Browser failed: {e}")
            return None
