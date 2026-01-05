from .base import BaseAgent
from image_gen import ImageGenManager
import json

class ImageGenAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Visual Content Creator",
            goal="Generate high-quality visuals for campaigns, social media, and landing pages.",
            provider=provider
        )
        self.image_manager = ImageGenManager()

    def think(self, context, instructions=None):
        """
        Enhances the user's prompt using the LLM and then generates the image.
        """
        # 1. Enhance Prompt using LLM
        enhancement_prompt = (
            "You are an expert AI Art Prompt Engineer. \n"
            "Refine the following request into a detailed DALL-E 3 / Stable Diffusion prompt.\n"
            "Include details about style, lighting, composition, and mood.\n"
            "Return JSON: {'enhanced_prompt': str, 'negative_prompt': str}"
        )
        
        full_context = f"User Request: {context}"
        if instructions:
            full_context += f"\nInstructions: {instructions}"

        response = self.provider.generate_json(f"{full_context}\n\n{enhancement_prompt}")
        enhanced_prompt = response.get('enhanced_prompt', context)
        
        # 2. Generate Image
        print(f"  [ImageAgent] meaningful prompt: {enhanced_prompt[:50]}...")
        try:
            image_url = self.image_manager.generate_image(enhanced_prompt)
            return {
                "status": "success",
                "original_prompt": context,
                "enhanced_prompt": enhanced_prompt,
                "image_url": image_url
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def generate_campaign_assets(self, campaign_context):
        """
        Generates a set of images for a campaign.
        """
        # Placeholder for batch logic
        pass
