import aiohttp
import asyncio
import random
import time
from config import config
from utils.logger_service import get_logger

logger = get_logger("SearchRouter")

class SearXNGRouter:
    """
    Manages access to SearXNG instances (local + public fallback).
    Tracks health, availability, and rotates requests.
    """
    def __init__(self):
        self.local_url = config.get("search", {}).get("searxng_url", "http://localhost:8081/search")
        
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
        candidates = []
        
        # 1. Always prioritize Local Instance (unless cooling down)
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
        """Report a failure to trigger cooldown."""
        print(f"⚠️ [SearchRouter] {url} failed with {status}. Cooling down for 5m.")
        self.cooldowns[url] = time.time() + self.cooldown_duration

    def report_success(self, url):
        """Clear cooldown if it was somehow cooling down? Logic mostly handled by usage."""
        if url in self.cooldowns:
            del self.cooldowns[url]

search_router = SearXNGRouter()
