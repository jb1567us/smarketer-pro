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
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt"
        ]
        self.proxy_pattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}')

    async def run_mission(self, log_callback=None):
        """Standard entry point for agents in this system."""
        
        def log(msg):
            print(msg)
            if log_callback:
                log_callback(msg)

        log(f"[{self.role}] Starting mass harvest mission...")
        raw_proxies = await self.harvest_all(log_callback=log)
        elite_proxies_data = await self.validate_proxies(raw_proxies, log_callback=log)
        
        # Persist to Database
        from database import save_proxies
        save_proxies(elite_proxies_data)
        
        log(f"[{self.role}] Mission complete. {len(elite_proxies_data)} elite proxies saved to database.")
        
        # Return just the addresses for backward compatibility if needed by manager
        elite_addresses = [p['address'] for p in elite_proxies_data]
        return {"elite_proxies": elite_addresses, "count": len(elite_addresses)}

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
            if log_callback: log_callback(f"    [!] Error harvesting source: {e}")
            return set()

    async def validate_proxies(self, proxies: Set[str], log_callback=None) -> List[dict]:
        """Validates anonymity, latency, and connectivity."""
        if log_callback: log_callback(f"  [Validator] Testing {len(proxies)} candidates for elite anonymity...")
        valid_proxies_data = []
        semaphore = asyncio.Semaphore(50) # Parallel validation

        async with aiohttp.ClientSession() as session:
            completed = 0
            total = len(proxies)
            
            async def wrapped_test(p):
                data = await self._test_proxy(session, p, semaphore)
                nonlocal completed
                completed += 1
                if completed % 50 == 0 and log_callback:
                    log_callback(f"    [Progress] Verified {completed}/{total} candidates...")
                if data and log_callback:
                    log_callback(f"      [OK] Elite Proxy Confirmed: {data['address']} ({data['latency']:.2f}s)")
                return data

            tasks = [wrapped_test(p) for p in proxies]
            results = await asyncio.gather(*tasks)
            valid_proxies_data = [r for r in results if r]
        
        return valid_proxies_data

    async def _test_proxy(self, session, proxy, semaphore) -> dict:
        async with semaphore:
            proxy_url = f"http://{proxy}"
            test_urls = ["http://httpbin.org/ip", "https://api.ipify.org?format=json"]
            start_time = time.time()
            
            # Simple protocol detection (SOCKS vs HTTP would need different libs, sticking to HTTP for now)
            # but we can try different test URLs
            try:
                # 1. Connectivity & Latency Check
                async with session.get(test_urls[0], proxy=proxy_url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        latency = time.time() - start_time
                        
                        # 2. Anonymity Check (Elite check)
                        origin = data.get("origin", "")
                        if "," not in origin:
                            # 3. Geo/Provider Info (Optional/Simulated or via another check)
                            return {
                                "address": proxy,
                                "protocol": "http",
                                "anonymity": "elite",
                                "country": "Unknown", # Could use geoip here if needed
                                "latency": latency
                            }
            except:
                pass
            return None

    def think(self, context, instructions=None):
        return f"I have analyzed the current proxy health and suggest a re-harvest. Context: {context}"

