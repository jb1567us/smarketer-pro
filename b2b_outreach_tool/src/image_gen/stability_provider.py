from .base import ImageProvider
import os
import requests
import base64

class StabilityImageProvider(ImageProvider):
    def __init__(self):
        self.api_key = os.getenv("STABILITY_API_KEY")
        self.api_host = "https://api.stability.ai"

    def generate_image(self, prompt: str, size: str = "1024x1024", **kwargs) -> str:
        if not self.api_key:
             raise RuntimeError("Stability API key not found.")
        
        url = f"{self.api_host}/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        body = {
            "steps": 40,
            "width": 1024,
            "height": 1024,
            "seed": 0,
            "cfg_scale": 5,
            "samples": 1,
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1
                }
            ],
        }

        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            json=body,
        )

        if response.status_code != 200:
             raise RuntimeError(f"Stability API Error: {response.text}")

        data = response.json()
        
        # Stability returns base64, so we save to disk
        image_data = data["artifacts"][0]["base64"]
        filename = f"generated_{os.urandom(4).hex()}.png"
        file_path = os.path.join("data", "generated_images", filename)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(image_data))
            
        return os.path.abspath(file_path)
