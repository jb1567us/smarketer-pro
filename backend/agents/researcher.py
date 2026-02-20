from .base import BaseAgent
from backend.llm_router import LLMTier

class ResearcherAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Researcher", role="Expert Web Researcher & Data Miner")

    async def think_async(self, payload: dict) -> dict:
        query = payload.get("query", "")
        self.log(f"Researching: {query}")
        
        prompt = f"Perform deep research on: {query}. Provide 3 key insights."
        # Use Economy tier for high-volume research tasks
        response = await self.ask_llm(prompt, tier=LLMTier.ECONOMY)
        
        return {"results": [{"content": response}], "count": 1}

    def run(self, query: str) -> str:
        # Sync wrapper if needed
        import asyncio
        return asyncio.run(self.think_async({"query": query}))["results"][0]["content"]
