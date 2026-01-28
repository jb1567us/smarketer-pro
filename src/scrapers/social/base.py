import asyncio
import aiohttp
import uuid
import random
from bs4 import BeautifulSoup
from config import config
from scraper import search_searxng
from utils.browser_manager import BrowserManager
from proxy_manager import proxy_manager
from scrapers.social.utils import parse_social_stats

class BaseSocialScraper:
    def __init__(self):
        self.browser_manager = None
        self.browser_semaphore = asyncio.Semaphore(5)

    async def _get_browser(self):
        if not self.browser_manager:
            self.browser_manager = BrowserManager(session_id="social_scraper")
            await self.browser_manager.launch(headless=True)
        return self.browser_manager.page

    async def close(self):
        if self.browser_manager:
            await self.browser_manager.close()

    async def smart_scrape(self, query_or_url, platform):
        """The core multi-method scraping flow."""
        target_type = "url" if query_or_url.startswith("http") else "handle"
        target_url = query_or_url if target_type == "url" else self.construct_url(query_or_url)

        # 1. Start Parallel Tasks (Dork + Lightweight HTTP)
        dork_task = asyncio.create_task(self.try_dork_search(query_or_url, platform))
        http_task = None
        if target_url:
            http_task = asyncio.create_task(self.try_lightweight_scrape(target_url))

        dork_results, http_results = await asyncio.gather(
            dork_task, 
            http_task if http_task else asyncio.sleep(0, result=None), 
            return_exceptions=True
        )

        if isinstance(dork_results, Exception): dork_results = None
        if isinstance(http_results, Exception): http_results = None

        # 2. X-Ray Fast Track
        if dork_results and dork_results.get("extracted_stats"):
            return {**dork_results, "status": "success", "method": "xray_fast_track"}

        # 3. HTTP Fast Track
        if http_results and http_results.get("status") == "success":
            return http_results

        # 4. Fallback: Browser Scrape
        if target_url:
            async with self.browser_semaphore:
                browser_data = await self.try_browser_scrape(target_url, platform)
                if browser_data: return browser_data

        if dork_results:
            return {**dork_results, "status": "partial_success"}

        return {"error": "All scraping methods failed.", "platform": platform}

    def construct_url(self, handle):
        """Platform specific URL construction."""
        return None

    async def try_lightweight_scrape(self, url):
        """Standard meta-tag extraction fallback."""
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        for attempt in range(3):
            proxy_url = proxy_manager.get_proxy(tier='elite')
            if not proxy_url: continue
            try:
                async with aiohttp.ClientSession(headers=headers) as session:
                    async with session.get(url, proxy=proxy_url, timeout=15) as response:
                        if response.status == 200:
                            text = await response.text()
                            soup = BeautifulSoup(text, 'html.parser')
                            meta = soup.find("meta", property="og:description")
                            if meta:
                                desc = meta.get("content", "")
                                stats = parse_social_stats(desc)
                                proxy_manager.report_result(proxy_url, success=True, latency=0.5) 
                                return {
                                    "source": "lightweight_http",
                                    "stats": desc,
                                    "extracted_stats": stats,
                                    "url": url,
                                    "status": "success"
                                }
                        elif response.status in [429, 403]:
                            proxy_manager.report_result(proxy_url, success=False)
            except:
                proxy_manager.report_result(proxy_url, success=False)
        return None

    async def try_dork_search(self, target, platform):
        site_map = {
            "linkedin": "site:linkedin.com/in",
            "twitter": "site:twitter.com",
            "tiktok": "site:tiktok.com/@",
            "threads": "site:threads.net/@",
            "reddit": "site:reddit.com",
            "instagram": "site:instagram.com"
        }
        if platform not in site_map: return None
        search_term = target.rstrip('/').split('/')[-1] if "http" in target else target
        dork = f'{site_map[platform]} "{search_term}"'
        if platform == "linkedin": dork += ' ("hiring" OR "founder" OR "owner" OR "ceo")'

        async with aiohttp.ClientSession() as session:
            results = await search_searxng(dork, session, num_results=5)
            if results:
                parsed_results = []
                global_stats = None
                for r in results:
                    snippet = r.get("content", "")
                    stats = parse_social_stats(snippet)
                    if stats and not global_stats: global_stats = stats
                    parsed_results.append({
                        "title": r.get("title"), "url": r.get("url"),
                        "snippet": snippet, "stats": stats
                    })
                return {
                    "source": "xray_dork", "results": parsed_results,
                    "extracted_stats": global_stats, "note": "Indexed pages found."
                }
        return None

    async def try_browser_scrape(self, url, platform):
        session_id = f"scrape_{uuid.uuid4().hex[:8]}"
        bm = BrowserManager(session_id=session_id)
        try:
            for attempt in range(4):
                proxy_url = proxy_manager.get_proxy(tier='elite') if attempt < 3 else None
                if attempt < 3 and not proxy_url: continue
                
                try:
                    proxy_cfg = {"server": proxy_url} if proxy_url else None
                    if proxy_url and "127.0.0.1:9050" in proxy_url:
                        await proxy_manager.rotate_tor_identity()
                    
                    page = await bm.launch(headless=True, proxy=proxy_cfg)
                    await page.goto(url, timeout=60000, wait_until="domcontentloaded")
                    await asyncio.sleep(2)
                    
                    await bm.solve_captcha_if_present()
                    
                    # Core extraction
                    content = await page.content()
                    title = await page.title()
                    
                    # Let subclasses handle specific logic
                    captured_data = await self.platform_extract(page, content)
                    
                    soup = BeautifulSoup(content, 'html.parser')
                    text_dump = soup.get_text(separator='\n', strip=True)[:5000]
                    
                    return {
                        "source": "browser_snapshot", "title": title, "url": url,
                        "raw_text_preview": text_dump, "html_snippet": content[:2000],
                        "platform": platform, "captured_hidden_data": captured_data
                    }
                except Exception as e:
                    if proxy_url: proxy_manager.report_result(proxy_url, success=False)
                    if attempt == 3: raise e
        finally:
            await bm.close()
        return None

    async def platform_extract(self, page, content):
        """Overridden by specific scrapers."""
        return {}
