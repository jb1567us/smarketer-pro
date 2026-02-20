import os
import psutil
import time
from collections import deque
from threading import Lock

class ProxyManager:
    """Manages a pool of proxies with rotation and health tracking."""
    def __init__(self, proxies: list[str] = None):
        self.proxies = deque(proxies or [])
        self.lock = Lock()
        self.health_map = {} # proxy -> success_count

    def get_proxy(self) -> str:
        with self.lock:
            if not self.proxies:
                return None
            proxy = self.proxies.popleft()
            self.proxies.append(proxy)
            return proxy

    def report_success(self, proxy: str):
        self.health_map[proxy] = self.health_map.get(proxy, 0) + 1

    def add_proxy(self, proxy: str):
        with self.lock:
            if proxy not in self.proxies:
                self.proxies.append(proxy)

class CaptchaHealer:
    """Queues requests that hit a CAPTCHA for prioritized resolution."""
    def __init__(self):
        self.queue = deque() # [(url, timestamp, payload)]
        self.lock = Lock()

    def add_to_queue(self, url: str, payload: dict = None):
        with self.lock:
            self.queue.append((url, time.time(), payload))

    def get_next_task(self):
        with self.lock:
            if self.queue:
                return self.queue.popleft()
            return None

    @property
    def queue_size(self):
        return len(self.queue)

class SystemMonitor:
    """Provides RAM-aware logic for adaptive concurrency."""
    @staticmethod
    def get_ram_usage_percent() -> float:
        return psutil.virtual_memory().percent

    @staticmethod
    def get_recommended_concurrency(base_rate: int = 4) -> int:
        """
        Calculates recommended worker threads based on available RAM.
        Pattern: 4 threads per GB of free RAM, but hard-capped by system state.
        """
        free_gb = psutil.virtual_memory().available / (1024**3)
        usage = psutil.virtual_memory().percent
        
        # Adaptive scaling
        if usage > 90:
            return 1 # Emergency throttle
        if usage > 75:
            return max(1, int(base_rate / 2))
            
        return max(1, int(free_gb * base_rate))

class SearXNGProvider:
    """Handles deep-web search queries via SearXNG instances."""
    def __init__(self, instances: list[str] = None):
        self.instances = instances or [
            "https://searx.be",
            "https://searxng.site",
            "https://priv.au"
        ]
        self.current_idx = 0
        self.lock = Lock()

    def get_next_instance(self) -> str:
        with self.lock:
            instance = self.instances[self.current_idx]
            self.current_idx = (self.current_idx + 1) % len(self.instances)
            return instance

class SearchRotator:
    """Orchestrates search backends to prevent footprinting."""
    def __init__(self):
        self.backends = ["Google", "SearXNG"]
        self.current_backend = "Google"
        self.lock = Lock()
        self.searx_provider = SearXNGProvider()

    def get_best_route(self) -> str:
        with self.lock:
            # Simple alternating logic for prototype
            route = self.current_backend
            self.current_backend = "SearXNG" if self.current_backend == "Google" else "Google"
            return route

# Singleton instances for use across the backend
proxy_manager = ProxyManager()
captcha_healer = CaptchaHealer()
system_monitor = SystemMonitor()
searx_provider = SearXNGProvider()
search_rotator = SearchRotator()
