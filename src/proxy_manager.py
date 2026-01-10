import aiohttp
import random
import asyncio
from config import config
import os
import subprocess
import yaml
import re
import sys
import time
import json
import argparse

class ProxyManager:
    def __init__(self):
        self.proxies = [] # Current working set
        self.bad_proxies = set()
        self.config = config.get("proxies", {})
        self.enabled = self.config.get("enabled", False)
        self.verification_url = "http://httpbin.org/ip"
        self._initialized = False
        # Enhanced source list
        self.public_sources = [
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
            "https://www.proxy-list.download/api/v1/get?type=https",
            "https://www.sslproxies.org/", 
            "https://free-proxy-list.net/",
            "https://www.us-proxy.org/"
        ]
        
        self.max_proxies = self.config.get("max_proxies", 50)
        
        # Defer DB load to first access
        # self._load_from_db()

    def _ensure_initialized(self):
        if not self._initialized:
            self._load_from_db()
            self._initialized = True

    async def test_against_target(self, proxy, target_url, keyword=None):
        """
        Tests if a proxy can successfully reach a target URL and find a keyword.
        Useful for 'Google-Passed' or platform-specific checks.
        """
        self._ensure_initialized()
        proxy_url = proxy if proxy.startswith("http") else f"http://{proxy}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(target_url, proxy=proxy_url, timeout=10) as response:
                    if response.status == 200:
                        if keyword:
                            text = await response.text()
                            return keyword in text
                        return True
        except:
            pass
        return False

    def _load_from_db(self):
        try:
            from database import get_best_proxies
            best = get_best_proxies(limit=self.max_proxies)
            self.proxies = [p['address'] for p in best]
            print(f"[{self.__class__.__name__}] Loaded {len(self.proxies)} elite proxies from database.")
        except Exception as e:
            print(f"Error loading proxies from DB: {e}")

    async def fetch_proxies(self, log_callback=None):
        """Fetches/Harvests proxies using multiple public sources."""
        self._ensure_initialized()
        if not self.enabled:
            return

        def log(msg):
            print(f"[{self.__class__.__name__}] {msg}")
            if log_callback: log_callback(msg)

        log("📡 Starting multi-source proxy harvest...")
        
        import asyncio
        import re
        all_fetched = set()
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in self.public_sources:
                tasks.append(self._fetch_source(session, url, log))
            
            # Use gather with return_exceptions=True to prevent one failure from stopping all
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for r in results:
                if isinstance(r, list):
                    all_fetched.update(r)
        
        log(f"📥 Fetched {len(all_fetched)} raw unique proxies. Testing availability...")
        
        if not all_fetched:
            log("❌ Critical: No proxies found from any source.")
            return

        # prioritized check
        test_candidates = list(all_fetched)
        random.shuffle(test_candidates)
        test_candidates = test_candidates[:300] # Cap at 300 to be fast
        
        working = await self.verify_proxies(test_candidates)
        
        if not working:
             log("⚠️ Validation yielded 0 working proxies.")
             return

        # Save to DB
        from database import save_proxies
        proxy_data = [{"address": p, "latency": 1.0, "anonymity": "unknown"} for p in working]
        save_proxies(proxy_data)
        
        self._load_from_db()
        log(f"✅ Harvest complete. {len(self.proxies)} working proxies loaded.")

    async def _fetch_source(self, session, url, logger=None):
        try:
            async with session.get(url, timeout=15) as response:
                if response.status == 200:
                    content = await response.text()
                    # Extract IP:PORT
                    matches = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}', content)
                    if logger and matches:
                        # Log only if substantial
                        pass 
                    return matches
                else:
                    if logger: logger(f"  [!] Failed to fetch {url[:30]}...: {response.status}")
        except Exception as e:
            if logger: logger(f"  [!] Error fetching {url[:30]}...: {str(e)[:50]}")
        return []

    async def _fallback_fetch(self):
        # Redirect to fetch_proxies since it now handles multiple sources
        await self.fetch_proxies()

    async def verify_proxies(self, proxy_list):
        working_proxies = []
        semaphore = asyncio.Semaphore(20)
        async def check(proxy):
            async with semaphore:
                if await self.verify_proxy(proxy):
                    working_proxies.append(proxy)
        await asyncio.gather(*(check(p) for p in proxy_list))
        return working_proxies

    async def verify_proxy(self, proxy):
        proxy_url = proxy if proxy.startswith("http") else f"http://{proxy}"
        try:
            async with aiohttp.ClientSession() as session:
                # Primary Check
                try:
                    async with session.get(self.verification_url, proxy=proxy_url, timeout=10) as response:
                        if response.status == 200:
                            return True
                except:
                    pass
                
                # Fallback Check
                try:
                    async with session.get("http://example.com", proxy=proxy_url, timeout=10) as response:
                        return response.status == 200
                except:
                    pass
        except Exception as e:
            # print(f"DEBUG: Proxy {proxy} failed completely: {e}")
            pass
        return False

    def get_proxy(self):
        """Returns a high-quality proxy from the available list."""
        self._ensure_initialized()
        if not self.enabled or not self.proxies:
            return None
        
        # Simple rotation for now, but we could make it smarter
        proxy = random.choice(self.proxies)
        if not proxy.startswith("http"):
             return f"http://{proxy}"
        return proxy

    def report_result(self, proxy, success: bool, latency: float = None):
        """Reports the result of using a proxy back to the manager and DB."""
        self._ensure_initialized()
        address = proxy.replace("http://", "").replace("https://", "")
        try:
            from database import update_proxy_health
            update_proxy_health(address, success=success, latency=latency)
            if not success:
                # Remove from current session set if it keeps failing
                self.bad_proxies.add(address)
                if address in self.proxies:
                    self.proxies.remove(address)
        except Exception as e:
            print(f"Error reporting proxy result: {e}")

    async def update_searxng_config(self):
        """Injects OR REMOVES proxies from SearXNG settings.yml based on self.enabled."""
        settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "searxng", "searxng", "settings.yml")
        docker_compose_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "searxng", "docker-compose.yaml")

        if not os.path.exists(settings_path):
            return False, f"Settings file not found at {settings_path}"

        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                content = f.read()

            proxy_list_yaml = "    all://:\n"
            if self.enabled and self.proxies:
                for p in self.proxies:
                    if not p.startswith("http"): p = f"http://{p}"
                    proxy_list_yaml += f"      - {p}\n"
            else:
                proxy_list_yaml = "    # Proxies disabled or pool empty\n"

            parts = content.split("outgoing:", 1)
            if len(parts) < 2:
                return False, "Could not find 'outgoing:' section in settings.yml"
                
            pre_outgoing = parts[0] + "outgoing:"
            post_outgoing = parts[1]
            
            new_proxies_block = "\n  proxies:\n" + proxy_list_yaml
            regex_proxies = r"(\s+proxies:\n\s+all://:\n(\s+-\s+.*)+)"
            
            if re.search(regex_proxies, post_outgoing, re.MULTILINE):
                 post_outgoing = re.sub(regex_proxies, new_proxies_block, post_outgoing, count=1)
            else:
                 post_outgoing = new_proxies_block + post_outgoing

            final_content = pre_outgoing + post_outgoing
            with open(settings_path, "w", encoding="utf-8") as f:
                f.write(final_content)

            print(f"[{self.__class__.__name__}] Updated settings.yml with {len(self.proxies)} proxies.")

            # Restart Docker
            cmd = ["docker", "compose", "-f", docker_compose_path, "restart", "searxng"]
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                 return True, f"Successfully updated SearXNG with pool of {len(self.proxies)} proxies."
            else:
                 return False, f"Updated config but Docker restart failed: {result.stderr}"

        except Exception as e:
            return False, f"Error updating SearXNG config: {e}"

    async def import_proxies(self, raw_text: str):
        pattern = re.compile(r'(?:http[s]?://)?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5})')
        matches = pattern.findall(raw_text)
        
        imported_count = 0
        proxy_data = []
        for p in matches:
            clean = p.replace("http://", "").replace("https://", "")
            proxy_data.append({"address": clean, "latency": 1.0, "anonymity": "unknown"})
            imported_count += 1
                
        if proxy_data:
            from database import save_proxies
            save_proxies(proxy_data)
            self._load_from_db()
            
        print(f"[{self.__class__.__name__}] Imported {imported_count} new proxies to database.")
        return imported_count, [p['address'] for p in proxy_data]

    def remove_proxy(self, proxy):
        address = proxy.replace("http://", "").replace("https://", "")
        self.report_result(proxy, success=False)

    async def enable_proxies(self):
        self._ensure_initialized()
        self.enabled = True
        print(f"[{self.__class__.__name__}] Enabling proxies...")
        
        if not self.proxies:
             print(f"[{self.__class__.__name__}] No proxies in memory. Forcing harvest...")
             await self.fetch_proxies()
        
        if self.proxies:
            success, msg = await self.update_searxng_config()
            return success, msg
        else:
            return False, "Failed to enable: Could not harvest any proxies."

    async def disable_proxies(self):
        self.enabled = False
        print(f"[{self.__class__.__name__}] Disabling proxies...")
        success, msg = await self.update_searxng_config()
        if success:
            return True, "Proxies disabled and removed from configuration."
        return False, f"Failed to disable proxies: {msg}"

    async def ensure_fresh_proxies(self, min_count=10, max_age_hours=24):
        """
        Ensures we have enough fresh proxies in the pool.
        Reloads from DB first. Only harvests if DB results are insufficient or too old.
        """
        self._ensure_initialized()
        if not self.enabled:
             return

        print(f"[{self.__class__.__name__}] Checking proxy freshness (Min: {min_count}, Max Age: {max_age_hours}h)...")
        
        # 1. Reload from DB to see current state
        self._load_from_db()
        
        # 2. Check if we meet the criteria
        # We need to know the age of the proxies. Let's add a quick check to database.py or just use the current pool if loaded
        # Actually, let's just check if we have enough proxies for now. 
        # For a more robust check, we'd query the DB for proxies checked within the last max_age_hours.
        
        needs_harvest = False
        if len(self.proxies) < min_count:
            print(f"[{self.__class__.__name__}] Low proxy count: {len(self.proxies)}/{min_count}. Needs harvest.")
            needs_harvest = True
        
        # TODO: Add logic to check timestamp of oldest/newest proxy in DB for real freshness
        
        if needs_harvest:
            print(f"[{self.__class__.__name__}] Initiating fresh harvest sequence with improved sources...")
            await self.fetch_proxies()
            
            if self.proxies:
                success, msg = await self.update_searxng_config()
                if not success:
                    print(f"[{self.__class__.__name__}] Warning: Failed to update SearXNG: {msg}")
            else:
                print(f"[{self.__class__.__name__}] Critical: Harvest yielded no proxies after validation.")
        else:
            print(f"[{self.__class__.__name__}] Proxy pool is sufficient and fresh. Skipping harvest.")

    def _check_status(self, max_age_hours=24):
        # Legacy stub
        return len(self.proxies) > 0

    def _save_status(self):
        # Legacy stub
        pass

# Global instance
proxy_manager = ProxyManager()

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    parser = argparse.ArgumentParser(description="Proxy Manager CLI")
    parser.add_argument("--check", action="store_true", help="Check freshness and update if stale")
    args = parser.parse_args()
    
    if args.check:
        try:
            asyncio.run(proxy_manager.ensure_fresh_proxies())
        except Exception as e:
            print(f"Startup check failed: {e}")
            sys.exit(1)


