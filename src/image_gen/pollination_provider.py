from .base import ImageProvider
import urllib.parse
import random
import requests
import os
import hashlib

class PollinationImageProvider(ImageProvider):
    def __init__(self):
        self.base_url = "https://image.pollinations.ai/prompt/"
    
    def generate_image(self, prompt: str, size: str = "1024x1024", **kwargs) -> str:
        """
        Generates an image using Pollination.ai.
        """
        # Parse size if needed, pollination uses query params width/height
        width, height = 1024, 1024
        if "x" in size:
            try:
                parts = size.split("x")
                width = int(parts[0])
                height = int(parts[1])
            except:
                pass

        # Clean prompt
        clean_prompt = prompt.replace('"', '').replace("'", "").strip()
        encoded_prompt = urllib.parse.quote(clean_prompt)
        seed = random.randint(0, 10000)
        
        # Build URL
        # Force model=unity for reliability and add nologo=true per designer.py logic
        image_url = f"{self.base_url}{encoded_prompt}?width={width}&height={height}&seed={seed}&model=unity&nologo=true"
        
        # Pollination URLs are direct image links, but sometimes we might want to save locally
        # to ensure they persist or if the UI has issues displaying external hotlinks.
        # For consistency with other providers (like Stability) that return paths or URLs,
        # we will attempt to download it to local storage.
        
        local_path = None
        try:
            # Create a local data directory if it doesn't exist
            data_dir = os.path.join(os.getcwd(), 'data', 'images')
            os.makedirs(data_dir, exist_ok=True)
            
            # Create a unique filename
            prompt_hash = hashlib.md5(clean_prompt.encode()).hexdigest()
            filename = f"pollination_{prompt_hash}_{seed}.png"
            local_path = os.path.join(data_dir, filename)
            
            # Download
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            with open(local_path, "wb") as f:
                f.write(response.content)
                
            # If successful, return the absolute local path for consistency
            return os.path.abspath(local_path)
            
        except Exception as e:
            print(f"  [PollinationProvider] Warning: Failed to download image locally ({e}). Returning URL.")
            return image_url
