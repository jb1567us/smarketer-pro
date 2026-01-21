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
        # config is imported globally. We'll use it live to avoid stale values.
        self.verification_url = "http://httpbin.org/ip"
        self.harvest_stats = {
            "is_active": False,
            "total": 0,
            "checked": 0,
            "found": 0,
            "start_time": 0,
            "etr": 0
        }
        self._initialized = False

    @property
    def enabled(self):
        return config.get("proxies", {}).get("enabled", False)

    @property
    def max_proxies(self):
        return config.get("proxies", {}).get("max_proxies", 1000)
        # Enhanced source list
        self.public_sources = [
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
            "https://www.sslproxies.org/", 
            "https://free-proxy-list.net/",
            "https://www.us-proxy.org/"
        ]
        
        
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
            max_p = config.get("proxies", {}).get("max_proxies", 1000)
            best = get_best_proxies(limit=max_p)
            self.proxies = [p['address'] for p in best]
            print(f"[{self.__class__.__name__}] Loaded {len(self.proxies)} elite proxies from database (Limit: {max_p}).")
        except Exception as e:
            print(f"Error loading proxies from DB: {e}")

    async def fetch_proxies(self, log_callback=None):
        """Fetches/Harvests proxies using multiple public sources."""
        self._ensure_initialized()
        if not config.get("proxies", {}).get("enabled", False):
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
        # Low yield for Instagram (0.8%), so we must test a HUGE chunk to get 200+
        test_candidates = test_candidates[:30000] 
        log(f"Testing {len(test_candidates)} candidates for tiered (Standard/Elite) compatibility (max 50 concurrent)...")
        
        # working is now list of dicts: {"address": p, "tier": level}
        working = await self.verify_proxies(test_candidates)
        
        if not working:
             log("⚠️ Validation yielded 0 working proxies.")
             return

        # Save to DB
        from database import save_proxies
        proxy_data = [{"address": p['address'], "latency": 1.0, "anonymity": p['tier']} for p in working]
        save_proxies(proxy_data, reset=True)
        
        self._load_from_db()
        elite_count = sum(1 for p in working if p['tier'] == 'elite')
        standard_count = len(working) - elite_count
        log(f"✅ Harvest complete. Found {elite_count} Elite and {standard_count} Standard proxies.")

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

    def start_harvest_bg(self):
        """Starts a massive fresh harvest in a background thread."""
        if self.harvest_stats["is_active"]:
            return False, "Harvest already in progress."

        import threading
        thread = threading.Thread(target=self._run_harvest_thread, daemon=True)
        thread.start()
        return True, "Background harvest started."

    def _run_harvest_thread(self):
        """Thread wrapper: creates and runs a new event loop for the async harvest."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.fetch_proxies())
            # Ensure SearXNG is updated after harvest
            loop.run_until_complete(self.update_searxng_config())
        except Exception as e:
            print(f"[ProxyManager] Background harvest error: {e}")
        finally:
            loop.close()

    async def _fallback_fetch(self):
        # Redirect to fetch_proxies since it now handles multiple sources
        await self.fetch_proxies()

    def ensure_fresh_bg(self, min_count=200, max_age_hours=4, force=False):
        """Starts a freshness check in a background thread to avoid blocking UI/Startup."""
        import threading
        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.ensure_fresh_proxies(min_count, max_age_hours, force))
            except Exception as e:
                print(f"[ProxyManager] Background freshness check error: {e}")
            finally:
                loop.close()
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return True

    async def verify_proxies(self, proxy_list):
        working_proxies = []
        # Concurrency 50 for Windows stability (prevents WinError 10054)
        semaphore = asyncio.Semaphore(50)
        
        # Telemetry Init
        self.harvest_stats["is_active"] = True
        self.harvest_stats["total"] = len(proxy_list)
        self.harvest_stats["checked"] = 0
        self.harvest_stats["found"] = 0
        self.harvest_stats["start_time"] = time.time()
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        connector = aiohttp.TCPConnector(limit=None, ssl=False) # Disable SSL verify for speed + proxies often have bad certs
        
        async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
            async def check(proxy):
                async with semaphore:
                    tier = await self.verify_proxy(proxy, session=session)
                    self.harvest_stats["checked"] += 1
                    if tier > 0:
                        tier_label = "elite" if tier == 2 else "standard"
                        working_proxies.append({"address": proxy, "tier": tier_label})
                        self.harvest_stats["found"] += 1
                    
                    # Estimate Time Remaining (ETR)
                    elapsed = time.time() - self.harvest_stats["start_time"]
                    if self.harvest_stats["checked"] > 0:
                        speed = self.harvest_stats["checked"] / elapsed # items/sec
                        remaining = self.harvest_stats["total"] - self.harvest_stats["checked"]
                        self.harvest_stats["etr"] = int(remaining / speed) if speed > 0 else 0

            await asyncio.gather(*(check(p) for p in proxy_list))
            
        self.harvest_stats["is_active"] = False
        return working_proxies

    async def verify_proxy(self, proxy, session=None):
        proxy_url = proxy if proxy.startswith("http") else f"http://{proxy}"
        
        # If no session provided, create a temporary one (backwards compatibility)
        should_close = False
        if session is None:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            session = aiohttp.ClientSession(headers=headers, connector=aiohttp.TCPConnector(ssl=False))
            should_close = True

        try:
            # 1. Elite Check (MUST BE HTTPS for Tunneling Support + Platform specific)
            # We verify against INSTAGRAM directly to ensure the proxy isn't banned there.
            try:
                target = "https://www.instagram.com"
                async with session.get(target, proxy=proxy_url, timeout=12, ssl=False) as response:
                    if response.status == 200:
                        server = response.headers.get("Server", "").lower()
                        if "cloudflare" not in server:
                            text = await response.text()
                            if "Instagram" in text or "instagram" in text:
                                return 2 # ELITE
            except:
                pass
            
            # 2. Standard Check (Basic connectivity)
            try:
                # Use a lightweight check for standard proxies
                async with session.get("http://httpbin.org/ip", proxy=proxy_url, timeout=10) as response:
                    if response.status == 200:
                        return 1 # STANDARD
            except:
                pass
        finally:
            if should_close:
                await session.close()
                
        return 0 # FAILED

    def get_proxy(self, tier=None):
        """
        Returns a high-quality proxy from the available list.
        :param tier: 'elite' or 'standard'
        """
        self._ensure_initialized()
        if not config.get("proxies", {}).get("enabled", False):
            return None
        
        pool = self.proxies
        if tier:
             # If tier is requested, we need to reload or filter.
             # self.proxies only stores addresses. We need the tiers.
             from database import get_best_proxies
             best = get_best_proxies(limit=100, min_anonymity=tier)
             pool = [p['address'] for p in best]

        if not pool:
            return None
            
        # Simple rotation for now
        proxy = random.choice(pool)
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
            if self.enabled:
                from database import get_best_proxies
                # Use Standard proxies for SearXNG to preserve Elite pool for verification
                std_proxies = get_best_proxies(limit=500, min_anonymity='standard')
                if not std_proxies:
                    # Fallback to all working if no standards found
                    std_proxies = get_best_proxies(limit=500)
                
                if std_proxies:
                    for p in std_proxies:
                        addr = p['address']
                        if not addr.startswith("http"): addr = f"http://{addr}"
                        proxy_list_yaml += f"      - {addr}\n"
                else:
                    proxy_list_yaml = "    # Proxies enabled but pool empty\n"
            else:
                proxy_list_yaml = "    # Proxies disabled\n"

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

    async def ensure_fresh_proxies(self, min_count=200, max_age_hours=4, force=False):
        """
        Ensures we have enough fresh proxies in the pool.
        Always prefers a fresh harvest if the pool is insufficient.
        """
        self._ensure_initialized()
        if not self.enabled and not force:
             return

        print(f"[{self.__class__.__name__}] Checking proxy freshness (Min: {min_count}, Max Age: {max_age_hours}h)...")
        
        # 1. Reload from DB
        self._load_from_db()

        # [Always Fresh] If we have fewer than min_count, we don't bother verifying old ones.
        # We just clear them and trigger a massive fresh harvest.
        if len(self.proxies) < min_count or force:
            print(f"[{self.__class__.__name__}] Proxy count low ({len(self.proxies)}/{min_count}). Initiating massive fresh harvest...")
            await self.fetch_proxies()
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


