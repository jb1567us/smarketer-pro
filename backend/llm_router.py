import time
import random
import logging
import asyncio
from enum import Enum
from typing import Dict, List, Any, Optional

class LLMTier(Enum):
    ECONOMY = "economy"
    PERFORMANCE = "performance"

class LLMProvider:
    def __init__(self, name: str, models: List[str], cooldown_seconds: int = 60):
        self.name = name
        self.models = models
        self.cooldown_seconds = cooldown_seconds
        self.last_failure_time = 0
        self.error_count = 0

    def is_available(self) -> bool:
        if self.last_failure_time == 0:
            return True
        return (time.time() - self.last_failure_time) > self.cooldown_seconds

    def report_failure(self):
        self.last_failure_time = time.time()
        self.error_count += 1
        logging.warning(f"Provider {self.name} blacklisted for {self.cooldown_seconds}s")

    def report_success(self):
        self.last_failure_time = 0
        # Slowly decay error count on success
        if self.error_count > 0:
            self.error_count -= 1

class SmartRouter:
    """
    Tiered routing with self-healing failover logic.
    Patterns from Smarketer Pro Technical Gem #2.
    """
    def __init__(self):
        self.tiers = {
            LLMTier.ECONOMY: [
                LLMProvider("Gemini-Flash", ["gemini-2.0-flash"]),
                LLMProvider("GPT-4o-Mini", ["gpt-4o-mini"]),
                LLMProvider("Groq-Llama", ["llama-3.3-70b-versatile"])
            ],
            LLMTier.PERFORMANCE: [
                LLMProvider("Claude-Sonnet", ["claude-3-5-sonnet-20241022"]),
                LLMProvider("GPT-4o", ["gpt-4o"]),
                LLMProvider("Gemini-Pro", ["gemini-1.5-pro"])
            ]
        }
        self.stats = {"total_requests": 0, "failovers": 0}

    def get_provider(self, tier: LLMTier) -> Optional[LLMProvider]:
        """Find the first available provider in the specified tier."""
        providers = self.tiers.get(tier, [])
        for provider in providers:
            if provider.is_available():
                return provider
        return None

    async def generate_text(self, prompt: str, tier: LLMTier = LLMTier.ECONOMY, **kwargs) -> str:
        self.stats["total_requests"] += 1
        
        # Try providers in order
        providers = self.tiers.get(tier, [])
        last_error = None

        for i, provider in enumerate(providers):
            if not provider.is_available():
                continue
            
            try:
                # In prototype mode, we simulate the LLM call or use local MCP
                # For this implementation, we simulate common behaviors 
                # but provide a hook for real calls.
                result = await self._mock_call(provider, i > 0)
                provider.report_success()
                return result
            except Exception as e:
                provider.report_failure()
                self.stats["failovers"] += 1
                last_error = e
                logging.error(f"Provider {provider.name} failed: {e}. Switching to next...")
        
        raise Exception(f"All providers in tier {tier.value} exhausted. Last error: {last_error}")

    async def _mock_call(self, provider: LLMProvider, is_fallback: bool) -> str:
        """Simulation logic for the prototype."""
        # Randomly simulate failures for testing if needed, or stick to healthy path
        # In a real app, this would use aiohttp to hit OpenAI/Anthropic/Gemini
        await asyncio.sleep(0.5)  # Simulate latency
        prefix = "[FALLBACK] " if is_fallback else ""
        return f"{prefix}Response from {provider.name} ({provider.models[0]})"

# Global instance for use across the backend
llm_router = SmartRouter()
