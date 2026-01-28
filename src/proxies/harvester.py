import aiohttp
import asyncio
import re
import hashlib
import random
import time
from database import update_proxy_source_status, get_proxy_sources, add_proxy_source
from config import config

class ProxyHarvester:
    def __init__(self, stats_ref=None):
        self.default_public_sources = [
            # Existing sources
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
            "https://www.sslproxies.org/", 
            "https://free-proxy-list.net/",
            "https://www.us-proxy.org/",
            # New high-quality sources
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
            "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
            "https://api.openproxylist.xyz/http.txt",
            "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt"
        ]
        self.stats = stats_ref or {}
        self.public_sources = []

    def sync_sources(self):
        """Loads sources from DB, seeding defaults if empty."""
        db_sources = get_proxy_sources(active_only=True)
        if not db_sources:
             for url in self.default_public_sources:
                 add_proxy_source(url)
             db_sources = get_proxy_sources(active_only=True)
        self.public_sources = [s['url'] for s in db_sources]
        return self.public_sources

    def is_public_ip(self, ip):
        """Checks if an IP is public (not private/local/reserved)."""
        import ipaddress
        try:
            ip_obj = ipaddress.ip_address(ip)
            return not (ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved)
        except ValueError:
            return False

    async def _fetch_source(self, session, url, logger=None):
        try:
            async with session.get(url, timeout=15) as response:
                if response.status == 200:
                    content = await response.text()
                    content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
                    
                    full_matches = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}', content)
                    filtered_matches = []
                    for m in full_matches:
                         ip_part = m.split(':')[0]
                         if self.is_public_ip(ip_part):
                             filtered_matches.append(m)
                    
                    update_proxy_source_status(url, success=True, content_hash=content_hash, yield_count=len(filtered_matches))
                    return filtered_matches
                else:
                    update_proxy_source_status(url, success=False)
                    if logger: logger(f"  [!] Failed to fetch {url[:30]}...: {response.status}")
        except Exception as e:
            if logger: logger(f"  [!] Error fetching {url[:30]}...: {str(e)[:50]}")
        return []

    async def harvest(self, log_callback=None):
        """Fetches/Harvests proxies using multiple public sources."""
        if not self.public_sources:
            self.sync_sources()

        def log(msg):
            if log_callback: log_callback(msg)

        log("📡 Starting multi-source proxy harvest...")
        
        all_fetched = set()
        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_source(session, url, log) for url in self.public_sources]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for r in results:
                if isinstance(r, list):
                    all_fetched.update(r)
        
        log(f"📥 Fetched {len(all_fetched)} raw unique proxies.")
        return list(all_fetched)
