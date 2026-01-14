from .base import ImageProvider
from config import config

class ImageGenManager:
    def __init__(self):
        self.providers = {}
        self._initialize_providers()

    def _initialize_providers(self):
        # Lazy load providers to avoid import errors if requirements are missing
        try:
            from .openai_provider import OpenAIImageProvider
            self.providers['openai'] = OpenAIImageProvider()
        except ImportError:
            pass

        try:
            from .stability_provider import StabilityImageProvider
            self.providers['stability'] = StabilityImageProvider()
        except ImportError:
            pass

        try:
            from .pollination_provider import PollinationImageProvider
            self.providers['pollination'] = PollinationImageProvider()
        except ImportError:
            pass

    def generate_image(self, prompt: str, provider_name: str = None, **kwargs) -> str:
        """
        Generates an image using the specified provider or the default one.
        """
        if not provider_name:
            provider_name = config.get('image_gen', {}).get('default_provider', 'pollination')
        
        provider = self.providers.get(provider_name)
        if not provider:
            # Fallback to first available
            if self.providers:
                provider_name = list(self.providers.keys())[0]
                provider = self.providers[provider_name]
            else:
                raise ValueError("No image generation providers available.")
        
        print(f"  [ImageGen] Generating image with {provider_name}...")
        return provider.generate_image(prompt, **kwargs)
