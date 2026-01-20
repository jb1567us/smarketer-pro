from .base import BaseAgent
from src.execution.gif_builder import create_pulsing_animation
import os

class DynamicGifAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Motion Graphics Designer",
            goal="Create eye-catching, branded animated GIFs for high-engagement social outreach.",
            provider=provider
        )

    def think(self, concept, instructions=None):
        """
        Creates a GIF based on the concept.
        """
        self.report_to_hub("ANIMATING", f"Building dynamic asset: {concept}")
        
        # Determine brand color from context if available
        brand_color = (0, 102, 204) # Smarketer Blue
        if self.context and "brand_color" in self.context.extra_context:
            brand_color = self.context.extra_context["brand_color"]

        # For Phase 2, we use a simple pulsing animation helper.
        # In a more advanced version, we'd use the LLM to generate 
        # the frame-by-frame draw instructions which this agent would execute.
        
        builder = create_pulsing_animation(concept, brand_color=brand_color)
        
        import hashlib
        data_dir = os.path.join(os.getcwd(), 'data', 'gifs')
        os.makedirs(data_dir, exist_ok=True)
        filename = f"engagement_{hashlib.md5(concept.encode()).hexdigest()[:8]}.gif"
        path = os.path.join(data_dir, filename)
        
        builder.save(path)
        
        self.report_to_hub("COMPLETED", f"GIF saved to {filename}")

        return {
            "type": "gif",
            "concept": concept,
            "path": path,
            "preview_url": f"Local Path: {path}"
        }
