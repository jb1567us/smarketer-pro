import os
import importlib
from datetime import datetime

class VideoGenManager:
    """
    Manages video generation providers and routes requests.
    Includes Smart Routing logic for browser-based free tiers.
    """
    
    def __init__(self, default_provider="mock"):
        self.providers = {}
        self.default_provider = default_provider
        self.usage_stats = {} # {provider_name: {date: count}}
        self._initialize_providers()

    def _initialize_providers(self):
        """
        Dynamically loads available providers based on configuration/environment.
        """
        # 1. Mock Provider (Always available)
        try:
            from .mock import MockProvider
            self.providers["mock"] = MockProvider()
        except ImportError:
            pass

        # 2. OpenAI (Sora/DALL-E)
        if os.getenv("OPENAI_API_KEY"):
            try:
                from .openai_video import OpenAIVideoProvider
                self.providers["openai"] = OpenAIVideoProvider(os.getenv("OPENAI_API_KEY"))
            except ImportError:
                print("Could not load OpenAI Video Provider")

        # 3. Browser Providers (Kling, Luma, Leonardo)
        try:
            from .browser_providers import KlingAIProvider, LumaProvider, LeonardoProvider
            self.providers["kling"] = KlingAIProvider()
            self.providers["luma"] = LumaProvider()
            self.providers["leonardo"] = LeonardoProvider()
        except ImportError as e:
            print(f"Could not load Browser Providers: {e}")

    def get_provider(self, provider_name=None):
        """
        Returns the requested provider instance.
        """
        if not provider_name or provider_name == "smart":
            # If explicit name not given, or 'smart' requested but we need a concrete instance for something generic
            # simpler to just return default or mock.
            # Smart routing is handled in 'route_request' usually, but if UI asks for a provider obj:
            return self.providers.get(self.default_provider, self.providers.get("mock"))
        
        return self.providers.get(provider_name, self.providers.get("mock"))

    def list_providers(self):
        """
        Returns a list of available provider keys.
        """
        keys = list(self.providers.keys())
        keys.insert(0, "smart") # Add Smart Router option
        return keys

    def smart_route(self, prompt, style, preferred_provider=None):
        """
        Selects the best provider based on prompt tags, style, and daily limits.
        """
        if preferred_provider and preferred_provider != "smart":
            return self.providers.get(preferred_provider)

        # 1. Analyze Requirements (Simple keyword matching)
        req_tags = []
        if "cinematic" in style.lower() or "movie" in prompt.lower():
            req_tags.append("cinematic")
        if "anime" in style.lower() or "cartoon" in prompt.lower():
            req_tags.append("animation")
        if "realistic" in style.lower() or "photo" in prompt.lower():
            req_tags.append("realistic")

        print(f"[SmartRouter] Request tags: {req_tags}")

        # 2. Score Providers
        best_provider = None
        best_score = -1
        
        today = datetime.now().strftime("%Y-%m-%d")

        for key, p in self.providers.items():
            if key == "mock" or key == "openai": continue # Skip paid/mock for smart free routing (unless configured)
            
            score = 0
            
            # Capability Match
            if hasattr(p, 'capabilities'):
                matches = sum(1 for t in req_tags if t in p.capabilities)
                score += matches * 10
                
                # Base preference for high limits
                if "high_daily_limit" in p.capabilities:
                    score += 5
            
            # Check Limits
            used = self.usage_stats.get(key, {}).get(today, 0)
            limit = getattr(p, 'daily_limit', 0)
            
            if used >= limit:
                print(f"[SmartRouter] Skipping {key}: Limit reached ({used}/{limit})")
                score = -100 # Penalize heavily or exclude
            
            print(f"[SmartRouter] {key} Score: {score}")
            
            if score > best_score:
                best_score = score
                best_provider = p

        if not best_provider:
             # Fallback to Kling if available (workhorse), else Mock
             best_provider = self.providers.get("kling", self.providers.get("mock"))

        print(f"[SmartRouter] Selected: {best_provider.name}")
        return best_provider

    def log_usage(self, provider_name):
        today = datetime.now().strftime("%Y-%m-%d")
        if provider_name not in self.usage_stats:
            self.usage_stats[provider_name] = {}
        
        current = self.usage_stats[provider_name].get(today, 0)
        self.usage_stats[provider_name][today] = current + 1
