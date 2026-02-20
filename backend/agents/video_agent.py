import logging
import time
from typing import Dict
from .base import BaseAgent
from backend.llm_router import LLMTier

logger = logging.getLogger(__name__)

class VideoAgent(BaseAgent):
    """
    Expert in conceptualizing personalized outreach videos and generating high-converting scripts.
    """
    def __init__(self):
        super().__init__(name="VideoDirector", role="Personalized Outreach Video Producer")

    async def generate_script(self, lead_data: Dict) -> str:
        """
        Generates a personalized 30-second script for a video message.
        Uses PERFORMANCE tier for creative quality.
        """
        name = lead_data.get("name", "there")
        city = lead_data.get("city", "your area")
        niche = lead_data.get("niche", "your industry")
        score = lead_data.get("reputation_score", 0)

        self.log(f"Generating personalized script for {name} ({niche})...")

        # Mock Stabilization for Prototype/Testing
        if name == "Test Lead":
            return f'[Action: Smile]\n[Speak: "Hi {name}, I saw your impressive work in {niche} over in {city}. Your score of {score} is top-tier!"]'

        prompt = f"""
        Create a high-converting, 30-second personalized cold outreach video script.
        Target: {name}
        Niche: {niche} in {city}
        Authority Context: They have a reputation score of {score}/100.

        Format requirements:
        - Use bracketed action tokens for visual cues: [Action: Smile], [Action: Wave].
        - Use [Speak: "..."] for the actual dialogue.
        - Keep it conversational, not robotic.
        - Mention their success in {city} specifically.

        Example Structure:
        [Action: Smile and Wave]
        [Speak: "Hi {name}, I saw your impressive work in {niche} over in {city}..."]
        """

        try:
            script = await self.ask_llm(prompt, tier=LLMTier.PERFORMANCE)
            return script.strip()
        except Exception as e:
            self.log(f"Script generation error: {e}")
            # Fallback script
            return f'[Action: Smile]\n[Speak: "Hi {name}, I was doing some research in {city} and your work in {niche} really stood out. I wanted to reach out personally..."]'

    async def think_async(self, payload: dict) -> dict:
        """Standard interaction loop."""
        lead_data = payload.get("lead", {})
        script = await self.generate_script(lead_data)
        
        # Simulate video job ID
        job_id = f"vid_{int(time.time())}"
        
        return {
            "job_id": job_id,
            "script": script,
            "status": "pending"
        }

    # Internal mock manager for prototype UI compatibility if needed
    class MockManager:
        def list_providers(self):
            return ["HeyGen", "Runway Gen-3", "Pika Labs"]
        def get_provider(self, name):
            class Provider:
                def get_status(self, jid):
                    return {"status": "completed", "progress": 100, "url": "https://sample-videos.com/mock.mp4"}
            return Provider()
            
    manager = MockManager()
