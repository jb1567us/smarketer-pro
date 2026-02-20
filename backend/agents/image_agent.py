from .manager import ManagerAgent

class ImageGenAgent(ManagerAgent):
    def __init__(self):
        super().__init__()
        self.role = "Visual Content Creator"
        self.goal = "Generate targeted visuals for marketing campaigns."

    async def generate_image(self, prompt, style="professional"):
        """Mock image generation."""
        return {
            "status": "success",
            "image_url": "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=800&auto=format&fit=crop&q=60",
            "enhanced_prompt": f"A professional {style} image representing {prompt}"
        }
