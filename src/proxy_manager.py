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
import hashlib
from database import update_proxy_source_status

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
            "found_elite": 0,
            "found_standard": 0,
            "start_time": 0,
            "etr": 0
        }
        self.tor_proxy = "socks5://127.0.0.1:9050"
        self.public_sources = []
        self.default_public_sources = [
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
        self._initialized = False
        self.last_freshness_check = 0 # Timestamp of last check
        self.tor_available = False
        self._check_tor_availability()

    def _check_tor_availability(self):
        """Checks if Tor SOCKS proxy is listening on 9050."""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2.0)
                result = s.connect_ex(('127.0.0.1', 9050))
                self.tor_available = (result == 0)
                if self.tor_available:
                     print(f"[{self.__class__.__name__}] Tor Circuit Breaker: ✅ ONLINE (Port 9050 open)")
                else:
                     print(f"[{self.__class__.__name__}] Tor Circuit Breaker: ❌ OFFLINE (Port 9050 closed). Elite mode disabled.")
        except Exception as e:
            print(f"[{self.__class__.__name__}] Tor Check Error: {e}")
            self.tor_available = False

    @property
    def enabled(self):
        return config.get("proxies", {}).get("enabled", False)

    @enabled.setter
    def enabled(self, value):
        if "proxies" not in config:
            config["proxies"] = {}
        config["proxies"]["enabled"] = value

    @property
    def max_proxies(self):
        return config.get("proxies", {}).get("max_proxies", 1000)
        
        
        # Defer DB load to first access
        # self._load_from_db()

    def _ensure_initialized(self):
        if not self._initialized:
            self._load_from_db()
            self._sync_sources_from_db()
            self._initialized = True

    def _sync_sources_from_db(self):
        """Loads sources from DB, seeding defaults if empty."""
        from database import get_proxy_sources, add_proxy_source
        
        # 1. Load from DB
        db_sources = get_proxy_sources(active_only=True)
        if not db_sources:
             print(f"[{self.__class__.__name__}] No sources in DB. Seeding defaults...")
             for url in self.default_public_sources:
                 add_proxy_source(url)
             db_sources = get_proxy_sources(active_only=True)

        self.public_sources = [s['url'] for s in db_sources]
        print(f"[{self.__class__.__name__}] Loaded {len(self.public_sources)} proxy sources from DB.")

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
            print(f"[{self.__class__.__name__}] Loaded {len(self.proxies)} proxies from database (Limit: {max_p}).")
        except Exception as e:
            print(f"Error loading proxies from DB: {e}")

    async def fetch_proxies(self, log_callback=None, verbose=False):
        """Fetches/Harvests proxies using multiple public sources."""
        self._ensure_initialized()
        if not config.get("proxies", {}).get("enabled", False):
            return

        def log(msg):
            print(f"[{self.__class__.__name__}] {msg}", flush=True)
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
        # [USER REQUEST] Unlocked: Check ALL candidates (targeting >41k requests)
        # test_candidates = test_candidates[:5000] 
        test_candidates = test_candidates # Full list 
        concurrency = config.get("proxies", {}).get("harvest_concurrency", 50)
        log(f"Testing {len(test_candidates)} candidates for tiered (Standard/Elite) compatibility (max {concurrency} concurrent)...")
        
        # working is now list of dicts: {"address": p, "tier": level}
        working = await self.verify_proxies(test_candidates, verbose=verbose)

        
        if not working:
             log("⚠️ Validation yielded 0 working proxies.")
             return

        # Save to DB
        from database import save_proxies
        proxy_data = [{"address": p['address'], "latency": 1.0, "anonymity": p['tier']} for p in working]
        # [USER REQUEST] Accumulate pool (reset=False) to reach 200/800 target
        save_proxies(proxy_data, reset=False)
        
        from database import save_setting
        save_setting('last_proxy_harvest_time', int(time.time()))
        
        self._load_from_db()
        elite_count = sum(1 for p in working if p['tier'] == 'elite')
        standard_count = len(working) - elite_count
        # Update SearXNG Config
        await self.update_searxng_config()
        
        log(f"✅ Harvest complete. Found {elite_count} Elite and {standard_count} Standard proxies.")

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
                    
                    # Calculate Hash
                    content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
                    
                    # Extract IP:PORT
                    # Update regex to be more robust if needed, but keeping existing one effectively
                    matches = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):\d{2,5}', content)
                    
                    # Filter private IPs
                    filtered_matches = []
                    # We need the full match (IP:PORT) but strict regex above only captured groups.
                    # Let's re-run regex or iterate differently.
                    # Actually, let's just grab full strings:
                    full_matches = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}', content)
                    
                    for m in full_matches:
                         ip_part = m.split(':')[0]
                         if self.is_public_ip(ip_part):
                             filtered_matches.append(m)
                    
                    # Update Reputation
                    update_proxy_source_status(url, success=True, content_hash=content_hash, yield_count=len(filtered_matches))
                    
                    if logger and filtered_matches:
                        # Log only if substantial
                        pass 
                    return filtered_matches
                else:
                    update_proxy_source_status(url, success=False)
                    if logger: logger(f"  [!] Failed to fetch {url[:30]}...: {response.status}")
        except Exception as e:
            if logger: logger(f"  [!] Error fetching {url[:30]}...: {str(e)[:50]}")
        return []

    def start_background_loop(self):
        """Starts the permanent background verification thread."""
        if self._initialized: return # Already running
        
        # Initial Load
        self._load_from_db()
        self._sync_sources_from_db()
        
        # [USER REQUEST] Internal loop disabled to prevent conflict with external worker
        # import threading
        # self.bg_thread = threading.Thread(target=self._background_loop, daemon=True, name="ProxyVerifier")
        # self.bg_thread.start()
        self._initialized = True
        print(f"[{self.__class__.__name__}] Internal Background Verifier DISABLED (Managed by external worker).")

    def _ensure_initialized(self):
        if not self._initialized:
             self.start_background_loop()

    def _background_loop(self):
        """
        Continuous loop to:
        1. Check pool health
        2. Rotate proxies if needed
        3. Verify existing proxies
        """
        while True:
            try:
                if self.enabled:
                    asyncio.run(self.ensure_fresh_proxies())
            except Exception as e:
                print(f"[{self.__class__.__name__}] Background Loop Error: {e}")
            
            # Sleep for 60 seconds
            time.sleep(60)

    # Clean up old methods as they are replaced by the loop
    def start_harvest_bg(self):
        return True, "Managed by Background Verifier now."
    
    def ensure_fresh_bg(self, *args, **kwargs):
        # Triggered by loop automatically
        return True

    async def verify_proxies(self, proxy_list, verbose=False):
        working_proxies = []
        
        # Get Concurrency Settings
        concurrency = config.get("proxies", {}).get("harvest_concurrency", 50)
        batch_size = config.get("proxies", {}).get("harvest_batch_size", 1000)
        
        # Concurrency 20 for Windows stability (default) - bumped to 50 via config
        semaphore = asyncio.Semaphore(concurrency)
        
        # Telemetry Init
        self.harvest_stats["is_active"] = True
        self.harvest_stats["total"] = len(proxy_list)
        self.harvest_stats["checked"] = 0
        self.harvest_stats["found"] = 0
        self.harvest_stats["found_elite"] = 0
        self.harvest_stats["found_standard"] = 0
        self.harvest_stats["start_time"] = time.time()
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        # Use a reasonable connection limit for the Windows networking stack
        connector = aiohttp.TCPConnector(limit=concurrency * 2, ssl=False, force_close=True) 
        
        async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
            async def check(proxy):
                try:
                    async with semaphore:
                        tier = await self.verify_proxy(proxy, session=session)
                        self.harvest_stats["checked"] += 1
                        if tier > 0:
                            tier_label = "elite" if tier == 2 else "standard"
                            working_proxies.append({"address": proxy, "tier": tier_label})
                            self.harvest_stats["found"] += 1
                            if tier == 2:
                                self.harvest_stats["found_elite"] += 1
                            else:
                                self.harvest_stats["found_standard"] += 1
                        
                        # Estimate Time Remaining (ETR)
                        elapsed = time.time() - self.harvest_stats["start_time"]
                        if self.harvest_stats["checked"] > 0:
                            speed = self.harvest_stats["checked"] / elapsed # items/sec
                            remaining = self.harvest_stats["total"] - self.harvest_stats["checked"]
                            self.harvest_stats["etr"] = int(remaining / speed) if speed > 0 else 0
                        
                        if verbose:
                             status_icon = "🟢" if tier > 0 else "🔴"
                             tier_str = "ELITE" if tier == 2 else ("STANDARD" if tier == 1 else "DEAD")
                             print(f"[{self.harvest_stats['checked']}/{self.harvest_stats['total']}] {status_icon} {proxy:<21} -> {tier_str}", flush=True)

                except (ConnectionResetError, aiohttp.ClientError, asyncio.TimeoutError):
                    # Silently handle common networking errors during mass check
                    self.harvest_stats["checked"] += 1
                    if verbose:
                         print(f"[{self.harvest_stats['checked']}/{self.harvest_stats['total']}] 🔴 {proxy:<21} -> TIMEOUT/ERR", flush=True)
                except OSError as e:
                    # Windows specific handling for [WinError 10054]
                    if getattr(e, 'winerror', 0) == 10054:
                        pass # Ignore forced connection close
                    else:
                        print(f"[ProxyManager] OS Error: {e}")
                    self.harvest_stats["checked"] += 1
                except Exception as e:
                    # Log unexpected errors
                    print(f"[ProxyManager] Unexpected verification error: {e}")
                    self.harvest_stats["checked"] += 1

            # Process in batches to keep the event loop responsive
            # batch_size defaults to 500, but can be bumped to 1000+ in config
            for i in range(0, len(proxy_list), batch_size):
                batch = proxy_list[i:i + batch_size]
                await asyncio.gather(*(check(p) for p in batch))
                # Small yield to let the loop breathe
                await asyncio.sleep(0.01)
                
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
            # [USER REQUEST] Strict Multi-Engine Validation
            # A proxy must pass ONE of these to be considered "Standard".
            
            is_standard = False
            
            # 1. Google Check (Most strict)
            try:
                async with session.get("https://www.google.com", proxy=proxy_url, timeout=10, ssl=False) as resp:
                    if resp.status == 200 and "google" in (await resp.text()).lower():
                        is_standard = True
            except: pass

            # 2. DuckDuckGo Check (Privacy engine support)
            if not is_standard:
                try:
                    async with session.get("https://duckduckgo.com", proxy=proxy_url, timeout=10, ssl=False) as resp:
                        if resp.status == 200:
                            is_standard = True
                except: pass

            # 3. Bing Check (Fallback)
            if not is_standard:
                try:
                    async with session.get("https://www.bing.com", proxy=proxy_url, timeout=10, ssl=False) as resp:
                         if resp.status == 200:
                             is_standard = True
                except: pass

            if is_standard:
                # 4. Elite Check (Instagram - for Social Scrapers)
                try:
                    target_ig = "https://www.instagram.com"
                    async with session.get(target_ig, proxy=proxy_url, timeout=12, ssl=False) as ig_resp:
                        if ig_resp.status == 200:
                            server = ig_resp.headers.get("Server", "").lower()
                            if "cloudflare" not in server:
                                ig_text = await ig_resp.text()
                                if "Instagram" in ig_text or "instagram" in ig_text:
                                    return 2 # ELITE
                except: pass
                
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
        ZERO LATENCY: Reads only from memory/DB.
        :param tier: 'elite' or 'standard'
        """
        self._ensure_initialized()
        if not config.get("proxies", {}).get("enabled", False):
            return None
        
        # 1. Try to get specific tier from DB
        if tier:
             from database import get_best_proxies
             # Query specifically for this tier
             best = get_best_proxies(limit=100, min_anonymity=tier)
             if best:
                 p = random.choice(best)
                 addr = p['address']
                 return f"http://{addr}" if not addr.startswith("http") else addr
        
        # 2. Fallback to general pool (self.proxies)
        if self.proxies:
            proxy = random.choice(self.proxies)
            if not proxy.startswith("http"):
                 return f"http://{proxy}"
            return proxy

        # 3. Last resort: Tor (Only if Circuit Breaker PASSED)
        if self.tor_available:
            return self.tor_proxy
            
        return None

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

    async def rotate_tor_identity(self):
        """
        Signals the Tor network to rotate the circuit and get a fresh IP.
        Requires Tor ControlPort (default 9051) to be open and authenticated (password or cookie).
        """
        import socket
        try:
            # Connect to Tor Control Port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("127.0.0.1", 9051))
                # authenticate - default empty or '""' if not set
                s.send(b'AUTHENTICATE ""\r\n')
                response = s.recv(1024)
                if b"250 OK" in response:
                    s.send(b"SIGNAL NEWNYM\r\n")
                    response = s.recv(1024)
                    if b"250 OK" in response:
                        print("[ProxyManager] Tor Identity Rotated! 🎭")
                        return True
            print("[ProxyManager] Tor Control connection failed - Check if ControlPort 9051 is enabled.")
        except Exception as e:
            print(f"[ProxyManager] Could not rotate Tor: {e}")
        return False

    async def update_searxng_config(self):
        """Injects OR REMOVES proxies from SearXNG settings.yml based on self.enabled."""
        settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "searxng", "searxng", "settings.yml")

        if not os.path.exists(settings_path):
            return False, f"Settings file not found at {settings_path}"

        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                content = f.read()

            proxy_list_yaml = "    all://:\n"
            if self.enabled:
                from database import get_best_proxies
                # [OPTMIZATION] Only use top-tier proxies
                # Criterion:
                # 1. Success rate > 80% (Proven)
                # 2. OR Anonymity == 'elite' (High Potential)
                # 3. OR Fresh (Total checks == 0) and just passed the harvester check.
                # [USER REQUEST] Pool scaled to 200 Elite + 800 Standard
                # [STABILITY FIX] Require min_success_count=1 to prevent unverified junk from breaking SearXNG
                elite_proxies = get_best_proxies(limit=200, min_anonymity='elite', min_success_count=1)
                standard_proxies = get_best_proxies(limit=800, min_anonymity='standard', min_success_count=1)
                
                # Combine distinct lists (handle potential overlaps if any, though tiering prevents it)
                combined_pool = elite_proxies + standard_proxies
                
                if combined_pool:
                    print(f"[{self.__class__.__name__}] Selected {len(combined_pool)} proxies ({len(elite_proxies)} Elite, {len(standard_proxies)} Standard) for SearXNG.")
                    for p in combined_pool:
                        addr = p['address']
                        if not addr.startswith("http"): addr = f"http://{addr}"
                        proxy_list_yaml += f"      - {addr}\n"
                else:
                    proxy_list_yaml = "    # No premium proxies available\n"
            else:
                proxy_list_yaml = "    # Proxies disabled\n"

            parts = content.split("outgoing:", 1)
            if len(parts) < 2:
                return False, "Could not find 'outgoing:' section in settings.yml"
                
            pre_outgoing = parts[0] + "outgoing:"
            post_outgoing = parts[1]
            
            # Improved Regex: Matches 'proxies:' indented by exactly 2 spaces (outgoing: level)
            regex_proxies = r"(\n  proxies:(?:\n(?:(?![ \t]*\w+:).)*)*)"
            
            # Reconstruct the block
            new_block = "\n  proxies:\n" + proxy_list_yaml
            
            # Remove ALL existing 'proxies:' blocks (cleanup duplicates/corruption)
            if re.search(regex_proxies, post_outgoing, re.MULTILINE | re.DOTALL):
                 post_outgoing = re.sub(regex_proxies, "", post_outgoing, flags=re.MULTILINE | re.DOTALL)
            
            # Prepend the new block to the clean section
            post_outgoing = new_block + post_outgoing

            final_content = pre_outgoing + post_outgoing
            
            # [ENHANCEMENT] Ensure JSON format is enabled in the search section
            if "formats:" in final_content:
                 final_content = final_content.replace("formats:\n    - html", "formats:\n    - html\n    - json")
            
            # [ENHANCEMENT] Disable limiter for local API usage
            if "limiter: true" in final_content:
                 final_content = final_content.replace("limiter: true", "limiter: false")

            with open(settings_path, "w", encoding="utf-8") as f:
                f.write(final_content)

            print(f"[{self.__class__.__name__}] Updated settings.yml with premium proxies.")

            # Restart via LiteDockManager (Handles both Docker and Sidecar)
            from utils.litedock_manager import litedock_manager
            success = litedock_manager.restart_searxng()
            
            if success:
                 return True, f"Successfully updated SearXNG with pool of {len(std_proxies)} premium proxies."
            else:
                 return False, "Updated config but SearXNG restart failed."

        except Exception as e:
            return False, f"Error updating SearXNG config: {e}"

    async def import_proxies(self, raw_text: str):
        pattern = re.compile(r'(?:http[s]?://)?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5})')
        matches = pattern.findall(raw_text)
        
        imported_count = 0
        proxy_data = []
        for p in matches:
            clean = p.replace("http://", "").replace("https://", "")
            ip_part = clean.split(':')[0]
            if self.is_public_ip(ip_part):
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

    async def ensure_fresh_proxies(self, min_count=200, max_age_hours=4, force=False, verbose=False):
        """
        Ensures we have enough fresh proxies in the pool.
        Always prefers a fresh harvest if the pool is insufficient or stale.
        """
        self._ensure_initialized()
        if not self.enabled and not force:
             return

        # [USER REQUEST] Continuous Mode: Reduced guard from 300s to 5s to allow tight-loop checking
        if not force and (time.time() - self.last_freshness_check < 5):
            return

        self.last_freshness_check = time.time()
        print(f"[{self.__class__.__name__}] Checking proxy freshness (Min: {min_count}, Max Age: {max_age_hours}h)...")
        
        # 1. Reload from DB
        self._load_from_db()

        # 2. Check for Elite availability if needed
        has_elites = False
        try:
            from database import get_best_proxies
            has_elites = len(get_best_proxies(limit=1, min_anonymity='elite')) > 0
        except:
            pass
            
        # 3. Check Pool Rotation (Time-based system-wide)
        from database import get_setting
        last_harvest = int(get_setting('last_proxy_harvest_time', 0))
        time_since_harvest = time.time() - last_harvest
        rotation_needed = time_since_harvest > (max_age_hours * 3600)
        
        if rotation_needed:
             print(f"[{self.__class__.__name__}] Pool Rotation Needed (Last harvest: {int(time_since_harvest/3600)}h ago).")

        # 4. Check Individual Freshness
        fresh_count = 0
        now = time.time()
        max_age_seconds = max_age_hours * 3600
        
        # self.proxies only has addresses, we need timestamps.
        # We need to query full proxy objects from DB to check time.
        # But for efficiency, let's just use get_best_proxies(limit=MAX)
        from database import get_best_proxies
        all_active = get_best_proxies(limit=2000)
        
        for p in all_active:
            last_checked = p.get('last_checked_at', 0) or 0
            fail_count = p.get('fail_count', 0) or 0
            
            # A proxy is "Fresh and Usable" if:
            # 1. Checked recently
            # 2. Not failing excessively (fail_count < 3) - REFINED
            if (now - last_checked) < max_age_seconds and fail_count < 3:
                fresh_count += 1
                
        print(f"[{self.__class__.__name__}] Fresh & Healthy Proxies: {fresh_count} / {len(all_active)}")

        # [Logic] Trigger harvest if:
        # A. Total active proxies < min_count
        # B. Fresh proxies < min_count (i.e. we have proxies but they are old or failing)
        # C. No elites found (quality gate)
        # D. Force flag is True
        
        is_stale = fresh_count < min_count
        is_insufficient = len(all_active) < min_count
        
        if is_insufficient or is_stale or not has_elites or rotation_needed or force:
            reasons = []
            if rotation_needed: reasons.append(f"rotation_needed ({int(time_since_harvest/60)}m > {max_age_hours*60}m)")
            if is_insufficient: reasons.append(f"insufficient_count ({len(all_active)} < {min_count})")
            if is_stale: reasons.append(f"stale_or_failing (healthy: {fresh_count} < {min_count})")
            if not has_elites: reasons.append("no_elites")
            if force: reasons.append("forced")
            
            reason_str = ", ".join(reasons)
            print(f"[{self.__class__.__name__}] Freshness check failed ({reason_str}). Initiating massive harvest...", flush=True)
            await self.fetch_proxies(verbose=verbose)
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
    parser.add_argument("--force", action="store_true", help="Force a fresh harvest")
    args = parser.parse_args()
    
    if args.check or args.force:
        try:
            asyncio.run(proxy_manager.ensure_fresh_proxies(force=args.force))
        except Exception as e:
            print(f"Startup check failed: {e}")
            sys.exit(1)


