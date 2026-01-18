import asyncio
import aiohttp
import re
import random
from urllib.parse import quote, urlparse
from bs4 import BeautifulSoup
from config import config
from scraper import search_searxng
from utils.browser_manager import BrowserManager
from proxy_manager import proxy_manager
import uuid

VALID_PLATFORMS = ["twitter", "linkedin", "tiktok", "instagram", "reddit", "youtube", "threads"]

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
        if "threads.net" in u: return "threads"
        return None

    def _construct_url(self, platform, handle):
        handle = handle.replace("@", "")
        if platform == "twitter": return f"https://twitter.com/{handle}"
        if platform == "tiktok": return f"https://tiktok.com/@{handle}"
        if platform == "instagram": return f"https://instagram.com/{handle}"
        if platform == "threads": return f"https://www.threads.net/@{handle}"
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
                "threads": "site:threads.net/@",
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
        Uses Playwright. 
        - Default: Render and dump HTML.
        - Threads: Extract hidden JSON state.
        - X (Twitter): Intercept GraphQL responses.
        """
        print(f"  [SocialScraper] Attempting Headless Browser (Playwright)...")
        import json
        
        platform = self._detect_platform(url)
        captured_data = {}

        # Use ephemeral session (Stealth: don't share cookies, use fresh ID)
        session_id = f"scrape_{uuid.uuid4().hex[:8]}"
        bm = BrowserManager(session_id=session_id)

        try:
            # Dynamic Proxy
            proxy_url = proxy_manager.get_proxy()
            proxy_cfg = {"server": proxy_url} if proxy_url else None
            
            if proxy_url:
                print(f"  [SocialScraper] Using Proxy: {proxy_url}")

            page = await bm.launch(headless=True, proxy=proxy_cfg)
            
            # Anti-detect measures (Extra headers)
            await page.set_extra_http_headers({
                "Accept-Language": "en-US,en;q=0.9"
            })

            # --- Platform Specific Setup BEFORE navigation ---
            if platform == "twitter":
                # Setup listener for X.com/Twitter GraphQL
                async def handle_response(response):
                    try:
                        if "UserBy" in response.url and response.status == 200:
                            # It's a profile data response
                            data = await response.json()
                            captured_data["twitter_graph_ql"] = data
                    except:
                        pass
                page.on("response", handle_response)

            # Navigate
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(2) # Initial render
            
            # Scroll for lazy load (generic)
            for _ in range(3):
                await page.mouse.wheel(0, 500)
                await asyncio.sleep(1)
            
            # Snapshot basic data
            title = await page.title()
            content = await page.content()
            
            # --- Platform Specific Extraction AFTER navigation ---
            
            # THREADS.NET Extraction
            if platform == "threads":
                # Look for the hidden JSON in script tags
                # <script type="application/json" data-sjs>
                try:
                    # We use a simple regex or soup to find the script content
                    # Using BeautifulSoup since we already have content, but executing generic JS in playwright is cleaner
                    # Let's try to find it in the content soup to avoid re-evaluating in page if possible, 
                    # but evaluating in page is more robust if DOM changed.
                    # Let's use BeautifulSoup on the 'content' we just grabbed.
                    soup = BeautifulSoup(content, 'html.parser')
                    scripts = soup.find_all('script', attrs={"type": "application/json", "data-sjs": True})
                    
                    for s in scripts:
                        if "follower_count" in s.text:
                            # Found a potential profile blob
                            try:
                                json_data = json.loads(s.text)
                                captured_data["threads_json"] = json_data
                                break
                            except:
                                continue
                except Exception as e:
                    print(f"  [SocialScraper] Threads extraction warning: {e}")

            # Intelligent Extraction (Simplified)
            soup = BeautifulSoup(content, 'html.parser')
            text_dump = soup.get_text(separator='\n', strip=True)[:5000] # Cap size
            
            result = {
                "source": "browser_snapshot",
                "title": title,
                "url": url,
                "raw_text_preview": text_dump,
                "html_snippet": content[:2000],
                "platform": platform
            }
            
            # Merge captured specific data
            if captured_data:
                result["captured_hidden_data"] = captured_data
                
            return result
            
        except Exception as e:
            print(f"  [SocialScraper] Browser failed: {e}")
            return None
        finally:
            await bm.close()
