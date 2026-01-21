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

def parse_social_stats(text):
    """
    Robust regex parser for social media stats in search engine snippets.
    Extracted from the 'content' field of SearXNG results.
    """
    if not text: return None
    
    stats = {}
    # Patterns for Followers: "10K Followers", "2.5M followers", "500 followers"
    follower_patterns = [
        r'([\d\.,KkMm]+?)\s+[Ff]ollowers',
        r'[Ff]ollowers:\s*([\d\.,KkMm]+)',
        r'([\d\.,KkMm]+?)\s+[Ss]ubscribers',
        r'([\d\.,KkMm]+?)\s+abonnés' # French for TikTok/Insta
    ]
    
    for pattern in follower_patterns:
        match = re.search(pattern, text)
        if match:
            stats["followers"] = match.group(1).upper()
            break
            
    # Patterns for Following/Posts if available
    following_match = re.search(r'([\d\.,KkMm]+?)\s+[Ff]ollowing', text)
    if following_match:
        stats["following"] = following_match.group(1).upper()
        
    posts_match = re.search(r'([\d\.,KkMm]+?)\s+[Pp]osts', text)
    if posts_match:
        stats["posts"] = posts_match.group(1).upper()

    return stats if stats else None

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
        
        # [Phase 1] FAST-TRACK: If X-Ray already found high-confidence stats, 
        # we can skip the browser entirely to save resources and avoid detection risk.
        if dork_results and dork_results.get("extracted_stats"):
             print(f"  [SocialScraper] ⚡ X-Ray Fast-Track! Found stats in search snippet.")
             return {
                 **dork_results,
                 "status": "success",
                 "method": "xray_fast_track"
             }

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

        # 2a. Strategy: Lightweight Scrape (Bypass Browser Tunnel Issues)
        # Verify confirmed that aiohttp works with our proxies, so we should try this first.
        low_cost_data = await self._try_lightweight_scrape(query_or_url)
        if low_cost_data:
             print(f"  [SocialScraper] ✅ Lightweight scrape succeeded! Skipping browser.")
             return low_cost_data

        # 3. Strategy: Throttled Browser (Only if lightweight failed)
        async with self.browser_semaphore:
            print(f"  [SocialScraper] Acquiring Browser Slot (Limit: 5)...")
            browser_data = await self._try_browser_scrape(query_or_url)
            
        if browser_data:
            return browser_data
            
        # Fallback to just dork data if browser failed
        if dork_results:
            # Enrich dork data with extracted stats if available
            return {**dork_results, "status": "partial_success"}

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

    async def _try_lightweight_scrape(self, url):
        """
        Attempts to scrape meta tags using aiohttp (High speed, low failure rate vs Playwright).
        Uses the shared ProxyManager to route requests.
        """
        if not url or "http" not in url: return None
        
        print(f"  [SocialScraper] Attempting Lightweight Scrape (aiohttp)...")
        from proxy_manager import proxy_manager
        
        # Retry loop for lightweight
        for attempt in range(3):
            # Explicitly request ELITE proxies for verification tasks
            proxy = proxy_manager.get_proxy(tier='elite')
            if not proxy: 
                # If no proxy, we can try direct IF safe, otherwise fail
                return None 

            try:
                # Use same headers as the successful verification
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
                
                async with aiohttp.ClientSession(headers=headers) as session:
                    async with session.get(url, proxy=proxy, timeout=10) as response:
                        if response.status == 200:
                            text = await response.text()
                            
                            # Extract Follower Count from Meta Tags
                            # <meta content="105K Followers, 107 Following, 1,203 Posts..." property="og:description" />
                            soup = BeautifulSoup(text, 'html.parser')
                            meta = soup.find("meta", property="og:description")
                            if meta:
                                desc = meta.get("content", "")
                                if "Followers" in desc:
                                    print(f"    -> Found stats: {desc[:50]}...")
                                    return {
                                        "source": "lightweight_http",
                                        "stats": desc,
                                        "url": url,
                                        "status": "success"
                                    }
                            # If we got 200 but no meta, might be a login page or captcha.
                            # But often Instagram public profiles DO return og:meta even if some content is gated.
                            # If we fail to find it, we proceed to browser.
                        else:
                             # print(f"    -> Status {response.status}")
                             pass

            except Exception as e:
                # print(f"    -> Error: {e}")
                pass
                
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
                "reddit": "site:reddit.com",
                "instagram": "site:instagram.com"
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
                 # [Phase 1] Extract Stats from Snippets
                 parsed_results = []
                 global_stats = None
                 
                 for r in results:
                     snippet = r.get("content", "")
                     stats = parse_social_stats(snippet)
                     if stats and not global_stats:
                         global_stats = stats # Take the first high-confidence match
                     
                     parsed_results.append({
                         "title": r.get("title"),
                         "url": r.get("url"),
                         "snippet": snippet,
                         "stats": stats
                     })

                 return {
                     "source": "xray_dork",
                     "results": parsed_results,
                     "extracted_stats": global_stats,
                     "note": "Indexed pages found and parsed."
                 }
        return None

        return None

    async def perform_warmup(self, page):
        """
        [Phase 4] Humanoid Warmup
        Visits safe sites to build cookie history and mimic organic behavior.
        """
        warmup_sites = [
            "https://www.wikipedia.org",
            "https://news.ycombinator.com",
            "https://github.com",
            "https://www.reddit.com"
        ]
        
        # Pick 1-2 random sites
        sites = random.sample(warmup_sites, k=random.randint(1, 2))
        print(f"  [SocialScraper] 🔥 Performing Humanoid Warmup on {len(sites)} sites...")
        
        for site in sites:
            try:
                await page.goto(site, wait_until='domcontentloaded', timeout=15000)
                await asyncio.sleep(random.uniform(2, 5)) 
                # Random scroll
                await page.mouse.wheel(0, random.randint(200, 600))
                await asyncio.sleep(random.uniform(1, 3))
            except:
                continue

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
            # Anti-detect measures (Extra headers)
            # Retry Loop
            max_retries = 3
            last_error = None
            
            for attempt in range(max_retries + 1):
                try:
                    # Dynamic Proxy (Rotate each attempt)
                    proxy_cfg = None
                    if attempt < max_retries:
                         proxy_url = proxy_manager.get_proxy(tier='elite')
                         if proxy_url:
                             proxy_cfg = {"server": proxy_url} 
                             print(f"  [SocialScraper] Attempt {attempt+1}/{max_retries} Using Proxy: {proxy_url}")
                             
                             # [Phase 3] Rotate Tor Identity if we are using Tor fallback
                             if "127.0.0.1:9050" in proxy_url:
                                 await proxy_manager.rotate_tor_identity()
                    else:
                         # [Safety] Do NOT fall back to direct connection for Instagram to protect User IP.
                         # print(f"  [SocialScraper] Proxies exhausted. Aborting to prevent IP ban.")
                         raise Exception("All proxies failed. Direct connection disabled for safety.")
                    
                    # Launch fresh for each attempt to avoid pollution
                    # Note: launching browser is expensive, so ideally we just new_context, 
                    # but for proxy rotation we need launch or specific context options.
                    # BM handles launch idempotency, but we need to force new proxy.
                    # Actually BM.launch creates a browser. We might need to close it to switch proxy easily 
                    # or just use context-level proxy if supported (Playwright supports browser-level mostly).
                    
                    # If a browser instance exists from a previous (failed) attempt, close it
                    if bm.browser:
                        await bm.close()
                        # Re-init fresh manager to clear any internal state
                        bm = BrowserManager(session_id=session_id)
                        
                    page = await bm.launch(headless=True, proxy=proxy_cfg)
                    # Sync local to instance (optional, but good for cleanup)
                    self.browser_manager = bm 

                    # [Phase 4] Perform Warmup before the real target
                    # But only if it's the first attempt or proxy changed
                    await self.perform_warmup(page)
            
                    await page.set_extra_http_headers({
                        "Accept-Language": "en-US,en;q=0.9"
                    })
                    
                    # Break if successful launch (we continue to nav below)
                    break
                except Exception as e:
                    print(f"  [SocialScraper] Proxy attempt failed: {e}")
                    last_error = e
                    if attempt == max_retries:
                        raise last_error

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

            # META TAG FOLLOWER EXTRACTION (Universal Fallback)
            # Works well for Instagram, TikTok, LinkedIn, Twitter which often put "X Followers" in og:description
            try:
                soup = BeautifulSoup(content, 'html.parser')
                og_desc = soup.find("meta", property="og:description")
                if og_desc and og_desc.get("content"):
                    desc_text = og_desc["content"]
                    # Regex to capture "10K Followers" or "200 Followers"
                    # Matches "10K Followers" or "10K followers" or "10K subscribers"
                    follower_match = re.search(r'([0-9\.,KkMm]+?)\s+(?:Followers|followers|Subscribers|subscribers)', desc_text)
                    if follower_match:
                        raw_count = follower_match.group(1)
                        captured_data["follower_count_raw"] = raw_count
                        print(f"  [SocialScraper] Extracted Followers: {raw_count} (from og:description)")
            except Exception as e:
                print(f"  [SocialScraper] Meta tag extraction warning: {e}")


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
