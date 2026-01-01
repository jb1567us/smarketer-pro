from .base import BaseAgent
import urllib.parse
import random

class GraphicsDesignerAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Creative Visual Designer",
            goal="Generate high-quality, relevant visual assets for marketing campaigns using generative AI.",
            provider=provider
        )

    def think(self, context):
        """
        Context: The concept or description of the image needed.
        Returns: A URL to the generated image.
        """
        # 1. Refine the prompt using LLM to be "Stable Diffusion friendly"
        refine_prompt = (
            f"Convert this concept into a detailed, high-quality image generation prompt for Stable Diffusion.\n"
            f"Concept: {context}\n"
            "Focus on lighting, style (e.g. photorealistic, cinematic, corporate memphis), and composition.\n"
            "Return ONLY the prompt string, no quotes or explanation."
        )
        
        image_prompt = self.provider.generate_text(refine_prompt).strip()
        
        # 2. Generate Image URL (using Pollinations.ai for free generation)
        # API Format: https://pollinations.ai/p/{prompt}?width={w}&height={h}&seed={seed}
        
        encoded_prompt = urllib.parse.quote(image_prompt)
        seed = random.randint(0, 10000)
        
        image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=576&seed={seed}&model=flux"
        
        return {
            "revised_prompt": image_prompt,
            "image_url": image_url,
            "description": context
        }
