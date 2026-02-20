import json
import logging
from typing import List, Dict, Any, Optional
from .base import BaseAgent, LLMTier

logger = logging.getLogger(__name__)

class VisualContentAgent(BaseAgent):
    """
    Agent responsible for designing visual layouts (Carousels/Infographics).
    """
    def __init__(self):
        super().__init__(
            name="Vinci",
            role="Creative Director specializing in B2B visual storytelling and social media design."
        )

    async def generate_carousel_layout(self, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Translates raw data into a sequence of high-impact carousel slides.
        """
        prompt = f"""
        Design a 5-slide B2B LinkedIn carousel based on the following input:
        {json.dumps(context_data, indent=2)}

        The objective is to position our solution as the perfect fit for this prospect's current market situation.

        For each slide, provide:
        1. Title (Hooky and bold)
        2. Body Text (Punchy, value-driven)
        3. Visual Icon (e.g. 'rocket', 'target', 'shield', 'chart-bar')
        4. Hex Color (Brand-compliant vibrant B2B colors like #3b82f6 blue, #10b981 green, #8b5cf6 purple)

        Return the result ONLY as a JSON list of objects.
        Example:
        [
          {{"title": "Global Expansion", "body": "Why your niche is the next frontier.", "icon": "globe", "hex_color": "#3b82f6"}},
          ...
        ]
        """
        
        self.log(f"Designing carousel for {context_data.get('name', 'Market Event')}...")
        
        try:
            response = await self.ask_llm(prompt, tier=LLMTier.PERFORMANCE)
            # Clean response if LLM added markdown blockers
            clean_json = response.strip()
            if "```json" in clean_json:
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_json:
                clean_json = clean_json.split("```")[1].split("```")[0].strip()
                
            slides = json.loads(clean_json)
            return slides
        except Exception as e:
            self.log(f"Error generating visual layout: {e}")
            return [
                {"title": "Opportunity Detected", "body": f"Strategic insight for {context_data.get('name', 'your niche')}.", "icon": "zap", "hex_color": "#3b82f6"},
                {"title": "The Solution", "body": "How our outreach engine scales your growth.", "icon": "rocket", "hex_color": "#10b981"},
                {"title": "Next Steps", "body": "Book a demo to see this in action.", "icon": "calendar", "hex_color": "#8b5cf6"}
            ]

# Singleton instance for general use
visual_agent = VisualContentAgent()
