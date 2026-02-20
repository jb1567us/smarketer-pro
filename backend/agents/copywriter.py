from .base import BaseAgent
from backend.llm_router import LLMTier

class CopywriterAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Copywriter", role="Elite B2B Copywriter & Conversion Specialist")

    async def think_async(self, prompt_text: str) -> dict:
        self.log("Drafting high-conversion copy...")
        
        # Use Performance tier for Elite Copywriting
        response = await self.ask_llm(prompt_text, tier=LLMTier.PERFORMANCE)
        
        return {"content": response}

    def run(self, prompt_text: str) -> str:
        import asyncio
        return asyncio.run(self.think_async(prompt_text))["content"]
