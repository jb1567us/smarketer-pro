from .base import ImageProvider
import os
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class OpenAIImageProvider(ImageProvider):
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY") # Or generic generic key
        if not api_key:
             # Try other keys if generic one missing, logic can be expanded
             pass
        self.client = OpenAI(api_key=api_key) if OpenAI and api_key else None

    def generate_image(self, prompt: str, size: str = "1024x1024", **kwargs) -> str:
        if not self.client:
            raise RuntimeError("OpenAI client not initialized (missing key or module).")
        
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024", # DALL-E 3 standard
            quality="standard",
            n=1,
        )
        
        return response.data[0].url
