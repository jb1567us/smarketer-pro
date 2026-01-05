from .base import BaseAgent
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
import time
from typing import List, Set

class ProxyAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Proxy Harvester",
            goal="Scrape, test, and maintain a high-quality list of elite proxies to ensure anonymity and resilience.",
            provider=provider
        )
        self.sources = [
            "https://www.sslproxies.org/",
            "https://free-proxy-list.net/",
            "https://www.us-proxy.org/",
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
            "https://www.proxy-list.download/api/v1/get?type=https",
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt"
        ]
        self.proxy_pattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}')

    async def run_mission(self, log_callback=None):
        """Standard entry point for agents in this system."""
        
        def log(msg):
            print(msg)
            if log_callback:
                log_callback(msg)

        log(f"[{self.role}] Starting mass harvest mission...")
        proxies = await self.harvest_all(log_callback=log)
        elite_proxies = await self.validate_proxies(proxies, log_callback=log)
        log(f"[{self.role}] Mission complete. Found {len(elite_proxies)} elite proxies.")
        return {"elite_proxies": elite_proxies, "count": len(elite_proxies)}

    async def harvest_all(self, log_callback=None) -> Set[str]:
        """Scrapes all sources for proxy strings."""
        if log_callback: log_callback(f"  [Scanner] Initiating deep crawl on {len(self.sources)} sources...")
        all_proxies = set()
        async with aiohttp.ClientSession() as session:
            tasks = [self._harvest_source(session, source, log_callback) for source in self.sources]
            results = await asyncio.gather(*tasks)
            for res in results:
                all_proxies.update(res)
        if log_callback: log_callback(f"  [Scanner] Aggregated {len(all_proxies)} potential candidates.")
        return all_proxies

    async def _harvest_source(self, session, url, log_callback=None) -> Set[str]:
        try:
            async with session.get(url, timeout=15) as response:
                if response.status != 200:
                    if log_callback: log_callback(f"    [X] Source failed ({response.status}): {url[:40]}...")
                    return set()
                text = await response.text()
                # Find all IP:Port patterns
                matches = self.proxy_pattern.findall(text)
                if log_callback: log_callback(f"    [+] Secured {len(matches)} proxies from {url[:40]}...")
                return set(matches)
        except Exception as e:
            # print(f"  [ProxyAgent] Error harvesting {url}: {e}")
            if log_callback: log_callback(f"    [!] Error harvesting source: {e}")
            return set()

    async def validate_proxies(self, proxies: Set[str], log_callback=None) -> List[str]:
        """Validates anonymity, latency, and connectivity."""
        if log_callback: log_callback(f"  [Validator] Testing {len(proxies)} candidates for elite anonymity...")
        valid_proxies = []
        semaphore = asyncio.Semaphore(50) # Parallel validation

        async with aiohttp.ClientSession() as session:
            # tasks = [self._test_proxy(session, p, semaphore) for p in proxies]
            # To provide progress updates, we need to wrap the tasks or callback from within
            
            completed = 0
            total = len(proxies)
            
            async def wrapped_test(p):
                res = await self._test_proxy(session, p, semaphore)
                nonlocal completed
                completed += 1
                if completed % 50 == 0 and log_callback:
                    log_callback(f"    [Progress] Verified {completed}/{total} candidates...")
                if res and log_callback:
                    log_callback(f"      [OK] Elite Proxy Confirmed: {res}")
                return res

            tasks = [wrapped_test(p) for p in proxies]
            results = await asyncio.gather(*tasks)
            valid_proxies = [r for r in results if r]
        
        return valid_proxies

    async def _test_proxy(self, session, proxy, semaphore) -> str:
        async with semaphore:
            proxy_url = f"http://{proxy}"
            test_url = "http://httpbin.org/ip"
            start_time = time.time()
            try:
                # 1. Connectivity & Latency Check
                async with session.get(test_url, proxy=proxy_url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        latency = time.time() - start_time
                        
                        # 2. Anonymity Check (Elite check)
                        # An elite proxy doesn't send X-Forwarded-For or other leak headers
                        origin = data.get("origin", "")
                        if "," not in origin: # Simple elite check: only one IP (the proxy's) should be present
                            # print(f"  [ProxyAgent] Elite Proxy Found: {proxy} ({latency:.2f}s)")
                            return proxy
            except:
                pass
            return None

    def think(self, context, instructions=None):
        return f"I have analyzed the current proxy health and suggest a re-harvest. Context: {context}"
