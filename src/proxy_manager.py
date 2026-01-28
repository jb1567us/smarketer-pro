import random
import asyncio
import os
import time
import re
from config import config
from database import get_best_proxies, update_proxy_health, save_proxies, get_setting, save_setting

# Modular Components
from proxies.harvester import ProxyHarvester
from proxies.validator import ProxyValidator
from proxies.config_editor import SearXNGConfigEditor

class ProxyManager:
    def __init__(self):
        self.proxies = [] # Current working set
        self.bad_proxies = set()
        self.tor_proxy = "socks5://127.0.0.1:9050"
        self._initialized = False
        self.last_freshness_check = 0
        self.tor_available = False
        
        # Dependency Injection (Internal)
        self.harvester = ProxyHarvester()
        self.validator = ProxyValidator()
        self.config_editor = SearXNGConfigEditor(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Link validator stats to self for UI compatibility
        self.harvest_stats = self.validator.stats
        
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
        except Exception:
            self.tor_available = False

    @property
    def enabled(self):
        return config.get("proxies", {}).get("enabled", False)

    @enabled.setter
    def enabled(self, value):
        if "proxies" not in config: config["proxies"] = {}
        config["proxies"]["enabled"] = value

    @property
    def max_proxies(self):
        return config.get("proxies", {}).get("max_proxies", 1000)

    def _ensure_initialized(self):
        if not self._initialized:
            self._load_from_db()
            self.harvester.sync_sources()
            self._initialized = True

    def _load_from_db(self):
        try:
            max_p = self.max_proxies
            best = get_best_proxies(limit=max_p)
            self.proxies = [p['address'] for p in best]
            print(f"[{self.__class__.__name__}] Loaded {len(self.proxies)} proxies from database.")
        except Exception as e:
            print(f"Error loading proxies from DB: {e}")

    async def fetch_proxies(self, log_callback=None, verbose=False):
        """Fetches/Harvests proxies and validates them."""
        self._ensure_initialized()
        if not self.enabled or config.get("proxies", {}).get("tor_only", False):
            return

        raw_proxies = await self.harvester.harvest(log_callback)
        if not raw_proxies: return

        # Validation
        working = await self.validator.verify_batch(raw_proxies, verbose=verbose)
        if working:
            proxy_data = [{"address": p['address'], "latency": 1.0, "anonymity": p['tier']} for p in working]
            save_proxies(proxy_data, reset=False)
            save_setting('last_proxy_harvest_time', int(time.time()))
            self._load_from_db()
            await self.update_searxng_config()
            
            elite_count = sum(1 for p in working if p['tier'] == 'elite')
            if log_callback:
                log_callback(f"✅ Harvest complete. Found {elite_count} Elite and {len(working)-elite_count} Standard proxies.")

    async def update_searxng_config(self):
        return self.config_editor.update_config(enabled=self.enabled, tor_available=self.tor_available)

    def get_proxy(self, tier=None):
        self._ensure_initialized()
        if not self.enabled: return None
        
        if tier:
             best = get_best_proxies(limit=100, min_anonymity=tier)
             if best:
                 addr = random.choice(best)['address']
                 return f"http://{addr}" if not addr.startswith("http") else addr
        
        if self.proxies:
            proxy = random.choice(self.proxies)
            return f"http://{proxy}" if not proxy.startswith("http") else proxy

        return self.tor_proxy if self.tor_available else None

    def report_result(self, proxy, success: bool, latency: float = None):
        self._ensure_initialized()
        address = proxy.replace("http://", "").replace("https://", "")
        update_proxy_health(address, success=success, latency=latency)
        if not success:
            self.bad_proxies.add(address)
            if address in self.proxies: self.proxies.remove(address)

    async def rotate_tor_identity(self):
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("127.0.0.1", 9051))
                s.send(b'AUTHENTICATE ""\r\n')
                if b"250 OK" in s.recv(1024):
                    s.send(b"SIGNAL NEWNYM\r\n")
                    if b"250 OK" in s.recv(1024):
                        print("[ProxyManager] Tor Identity Rotated! 🎭")
                        return True
        except Exception as e:
            print(f"[ProxyManager] Could not rotate Tor: {e}")
        return False

    async def import_proxies(self, raw_text: str):
        pattern = re.compile(r'(?:http[s]?://)?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5})')
        matches = pattern.findall(raw_text)
        proxy_data = []
        for p in matches:
            clean = p.replace("http://", "").replace("https://", "")
            if self.harvester.is_public_ip(clean.split(':')[0]):
                proxy_data.append({"address": clean, "latency": 1.0, "anonymity": "unknown"})
        if proxy_data:
            save_proxies(proxy_data)
            self._load_from_db()
        return len(proxy_data), [p['address'] for p in proxy_data]

    async def enable_proxies(self):
        self._ensure_initialized()
        self.enabled = True
        if not self.proxies: await self.fetch_proxies()
        return await self.update_searxng_config()

    async def disable_proxies(self):
        self.enabled = False
        return await self.update_searxng_config()

    async def ensure_fresh_proxies(self, min_count=200, max_age_hours=4, force=False):
        self._ensure_initialized()
        if not self.enabled and not force: return
        if not force and (time.time() - self.last_freshness_check < 5): return
        self.last_freshness_check = time.time()
        
        self._load_from_db()
        last_harvest = int(get_setting('last_proxy_harvest_time', 0))
        rotation_needed = (time.time() - last_harvest) > (max_age_hours * 3600)
        
        all_active = get_best_proxies(limit=2000)
        fresh_count = sum(1 for p in all_active if (time.time() - (p.get('last_checked_at', 0) or 0)) < (max_age_hours * 3600) and (p.get('fail_count', 0) or 0) < 3)
        
        if fresh_count < min_count or rotation_needed or force:
            await self.fetch_proxies()

# Global Singleton
proxy_manager = ProxyManager()
