from typing import List, Dict, Any
import asyncio
from .base import BaseAgent
from backend.llm_router import LLMTier

class ManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Eugene", role="Chief Strategy Officer & System Master")

    async def collaborate_on_strategy(self, history: List[Dict[str, str]], user_input: str):
        """
        AI-to-AI collaboration logic for the Strategy War Room.
        Uses Performance tier for high-quality strategy refinement.
        """
        self.log(f"Collaborating on strategy: '{user_input[:30]}...'")
        
        prompt = f"Previous context: {history}\nNew idea: {user_input}\nRefine this into a 3-step action plan."
        
        # Use Performance tier for the Chief Strategy Officer
        response_text = await self.ask_llm(prompt, tier=LLMTier.PERFORMANCE)
        
        return {
            "role": "AI",
            "content": response_text,
            "agent_logs": [f"{self.name} analyzed market fit", "Strategy refined via Performance Tier"]
        }
