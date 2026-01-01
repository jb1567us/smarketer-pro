import aiohttp
import random
import asyncio
from config import config

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.bad_proxies = set()
        self.config = config.get("proxies", {})
        self.enabled = self.config.get("enabled", False)
        self.source_url = self.config.get("source_url", "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt")
        self.max_proxies = self.config.get("max_proxies", 50)
        self.verification_url = self.config.get("verification_url", "http://httpbin.org/ip")

    async def fetch_proxies(self):
        """Fetches proxies from the configured source."""
        if not self.enabled:
            print("Proxy usage is disabled in config.")
            return

        print(f"Fetching proxies from {self.source_url}...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.source_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        lines = content.splitlines()
                        # Simple parsing, assuming ip:port or ip:port per line
                        fetched = [line.strip() for line in lines if line.strip()]
                        print(f"Fetched {len(fetched)} proxies.")
                        
                        # Verify and keep only working ones (up to max_proxies)
                        # To save time, we might not verify ALL of them upfront in a real scenario,
                        # but for this implementation, let's verify a batch.
                        self.proxies = await self.verify_proxies(fetched[:self.max_proxies * 2])
                        print(f"Initialized with {len(self.proxies)} working proxies.")
                    else:
                        print(f"Failed to fetch proxies: {response.status}")
        except Exception as e:
            print(f"Error fetching proxies: {e}")

    async def verify_proxies(self, proxy_list):
        """Verifies a list of proxies concurrently."""
        working_proxies = []
        semaphore = asyncio.Semaphore(20) # Limit concurrency

        async def check(proxy):
            async with semaphore:
                if await self.verify_proxy(proxy):
                    working_proxies.append(proxy)

        await asyncio.gather(*(check(p) for p in proxy_list))
        return working_proxies[:self.max_proxies]

    async def verify_proxy(self, proxy):
        """Checks if a proxy is working by making a request to the verification URL."""
        # Ensure proxy has scheme
        if not proxy.startswith("http"):
             proxy_url = f"http://{proxy}"
        else:
             proxy_url = proxy

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.verification_url, proxy=proxy_url, timeout=5) as response:
                    return response.status == 200
        except:
            return False

    def get_proxy(self):
        """Returns a random proxy from the available list."""
        if not self.enabled or not self.proxies:
            return None
        
        proxy = random.choice(self.proxies)
        if not proxy.startswith("http"):
             return f"http://{proxy}"
        return proxy

    def remove_proxy(self, proxy):
        """Removes a bad proxy from the list."""
        # proxy string comes in as http://ip:port, our list has ip:port
        clean_proxy = proxy.replace("http://", "").replace("https://", "")
        if clean_proxy in self.proxies:
            self.proxies.remove(clean_proxy)
            self.bad_proxies.add(clean_proxy)
            print(f"Removed bad proxy: {clean_proxy}. Remaining: {len(self.proxies)}")

# Global instance
proxy_manager = ProxyManager()
