import aiohttp
import asyncio
import random
import time
import os
from config import config
from utils.logger_service import get_logger

logger = get_logger("SearchRouter")

class SearXNGRouter:
    """
    Manages access to SearXNG instances (local + public fallback).
    Tracks health, availability, and rotates requests.
    """
    def __init__(self):
        from utils.litedock_manager import litedock_manager
        
        # Check and ensure local infrastructure (Docker or Lite-Dock)
        litedock_manager.ensure_searxng()
        self.local_url = litedock_manager.get_local_url()
        
        # High-quality public instances (Subject to change, can be updated via config)
        self.public_instances = [
            "https://searx.be/search",
            "https://searx.work/search",
            "https://priv.au/search",
            "https://search.ononoki.org/search",
            "https://searx.aicampus.u-bordeaux.fr/search",
            "https://opnxng.com/search",
            "https://search.sapti.me/search",
            "https://searx.webheberg.center/search"
        ]
        
        # Track bad instances to avoid them temporarily
        # {url: timestamp_when_available_again}
        self.cooldowns = {} 
        self.cooldown_duration = 300 # 5 minutes

    def get_candidates(self):
        """Returns a list of URLs to try in order."""
        # Check environment - Default to 'local' (Strict Privacy)
        env = os.environ.get("ENVIRONMENT", "local").lower()
        strict_privacy = config.get("search", {}).get("strict_privacy", True)
        
        # Ensure infrastructure is ready if using local
        from utils.litedock_manager import litedock_manager
        if "localhost" in self.local_url or "127.0.0.1" in self.local_url:
             self.local_url = litedock_manager.get_local_url()
        
        candidates = []
        
        # 1. Always prioritize Local Instance
        if env == "local" or strict_privacy:
            # In strict mode, we NEVER return public instances
            if self._is_cooling_down(self.local_url):
                 # If local is dead, we prefer to FAIL than to leak data to public instances
                 # But we can try to return it anyway and let the caller fail, 
                 # triggering the auto-healing logic in report_failure
                 return [self.local_url] 
            return [self.local_url]
            
        # CLOUD/PROD LOGIC (Only reached if ENVIRONMENT != local AND strict_privacy = False):
        if not self._is_cooling_down(self.local_url):
            candidates.append(self.local_url)
        
        # 2. Add available public instances (shuffled for load balancing)
        available_public = [url for url in self.public_instances if not self._is_cooling_down(url)]
        random.shuffle(available_public)
        candidates.extend(available_public)
        
        # 3. Last resort: add cooked instances if everything else is down
        if not candidates:
             candidates = [self.local_url] + self.public_instances
             
        return candidates

    def _is_cooling_down(self, url):
        if url in self.cooldowns:
            if time.time() < self.cooldowns[url]:
                return True
            else:
                del self.cooldowns[url]
        return False

    def report_failure(self, url, status):
        """Report a failure to trigger cooldown. Has auto-recovery for local instance."""
        print(f"⚠️ [SearchRouter] {url} failed with {status}. Cooling down for 5m.")
        self.cooldowns[url] = time.time() + self.cooldown_duration
        
        # Auto-Healing Logic for Local SearXNG
        if url == self.local_url:
            self.local_failure_count = getattr(self, "local_failure_count", 0) + 1
            print(f"  [SearchRouter] Local Failure Count: {self.local_failure_count}/3")
            
            if self.local_failure_count >= 3:
                print("  [SearchRouter] 🚨 CRITICAL: Local SearXNG is failing consistently. Triggering EMERGENCY PROXY REFRESH...")
                self.local_failure_count = 0 # Reset
                
                # Import here to avoid circular dependency risk at top level if any
                from proxy_manager import proxy_manager
                
                # Fire and forget (or we could await if this was an async method, but report_failure is sync context usually)
                # But since report_failure is usually called from async context, we can use create_task
                try:
                    asyncio.create_task(proxy_manager.ensure_fresh_proxies(force=True))
                except Exception as e:
                    print(f"  [SearchRouter] Failed to trigger proxy refresh: {e}")

    def report_success(self, url):
        """Clear cooldown if it was somehow cooling down? Logic mostly handled by usage."""
        if url in self.cooldowns:
            del self.cooldowns[url]

search_router = SearXNGRouter()
