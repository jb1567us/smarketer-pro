from typing import List, Dict, Any, Optional
from backend.llm_router import llm_router, LLMTier

class BaseAgent:
    """Base class for all AI agents, providing tiered LLM access."""
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.status_callback = None

    def log(self, message: str):
        if self.status_callback:
            self.status_callback(f"[{self.name}] {message}")
        else:
            print(f"[{self.name}] {message}")

    async def ask_llm(self, prompt: str, tier: LLMTier = LLMTier.ECONOMY, system_prompt: Optional[str] = None) -> str:
        """Call the smart router to generate a response."""
        full_prompt = prompt
        if system_prompt or self.role:
            sys = system_prompt or f"You are {self.name}, {self.role}."
            full_prompt = f"SYSTEM: {sys}\nUSER: {prompt}"
            
        self.log(f"Requesting {tier.value} LLM...")
        return await llm_router.generate_text(full_prompt, tier=tier)
