import os
import importlib

class VideoGenManager:
    """
    Manages video generation providers and routes requests.
    """
    
    def __init__(self, default_provider="mock"):
        self.providers = {}
        self.default_provider = default_provider
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

        # 3. Luma Dream Machine
        if os.getenv("LUMA_API_KEY"):
            try:
                from .luma import LumaProvider
                self.providers["luma"] = LumaProvider(os.getenv("LUMA_API_KEY"))
            except ImportError:
                print("Could not load Luma Provider")

        # 4. Stability AI
        if os.getenv("STABILITY_API_KEY"):
            try:
                from .stability import StabilityProvider
                self.providers["stability"] = StabilityProvider(os.getenv("STABILITY_API_KEY"))
            except ImportError:
                print("Could not load Stability Provider")

    def get_provider(self, provider_name=None):
        """
        Returns the requested provider instance.
        """
        if not provider_name:
            provider_name = self.default_provider
        
        return self.providers.get(provider_name, self.providers.get("mock"))

    def list_providers(self):
        """
        Returns a list of available provider keys.
        """
        return list(self.providers.keys())
