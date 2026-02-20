import reflex as rx
import asyncio
import time
from typing import Dict, List, Any
from pydantic import BaseModel
from .base import BaseState
from backend.llm_router import llm_router, LLMTier

class ProviderInfo(BaseModel):
    """Model for LLM provider health status."""
    name: str = ""
    available: bool = True
    cooldown: int = 0
    tier: str = ""

class LLMState(BaseState):
    """State for tracking LLM Router health and stats."""
    total_requests: int = 0
    failovers: int = 0
    
    # Provider health flags for the UI
    provider_health: Dict[str, Dict[str, Any]] = {}
    provider_names: List[str] = []
    # Typed list for rx.foreach stability
    provider_info_list: List[ProviderInfo] = []
    
    active_tier: str = "Economy"
    last_response: str = ""

    def update_router_stats(self):
        """Update local state with backend router stats."""
        self.total_requests = llm_router.stats["total_requests"]
        self.failovers = llm_router.stats["failovers"]
        
        health_snapshot = {}
        for tier_enum, providers in llm_router.tiers.items():
            for p in providers:
                is_avail = p.is_available()
                wait_time = 0
                if not is_avail:
                    wait_time = int(p.cooldown_seconds - (time.time() - p.last_failure_time))
                    wait_time = max(0, wait_time)
                
                health_snapshot[p.name] = {
                    "available": is_avail,
                    "cooldown": wait_time,
                    "tier": tier_enum.value
                }
        self.provider_health = health_snapshot
        self.provider_names = list(health_snapshot.keys())
        self.provider_info_list = [
            ProviderInfo(
                name=k,
                available=v["available"],
                cooldown=v["cooldown"],
                tier=v["tier"]
            )
            for k, v in health_snapshot.items()
        ]

    @rx.event(background=True)
    async def poll_router_health(self):
        """Periodically refresh router health snapshot."""
        while self.is_polling:
            async with self:
                self.update_router_stats()
            await asyncio.sleep(5)

    async def run_test_request(self, tier_name: str = "Economy"):
        """Simulate an LLM request via the smart router."""
        tier = LLMTier.ECONOMY if tier_name.lower() == "economy" else LLMTier.PERFORMANCE
        self.active_tier = tier_name
        self.last_response = "Thinking..."
        yield
        
        try:
            resp = await llm_router.generate_text("Test prompt", tier=tier)
            self.last_response = resp
            self.update_router_stats()
        except Exception as e:
            self.last_response = f"ERROR: {str(e)}"
        yield

    def reset_blacklists(self):
        """Clear all provider cooldowns for testing."""
        for tier_enum, providers in llm_router.tiers.items():
            for p in providers:
                p.last_failure_time = 0
        self.update_router_stats()
        self.add_log("LLM Router blacklists reset.")

    def simulate_failure(self, provider_name: str):
        """Force a failure report for a specific provider."""
        for tier_enum, providers in llm_router.tiers.items():
            for p in providers:
                if p.name == provider_name:
                    p.report_failure()
        self.update_router_stats()
        self.add_log(f"Simulated failure for {provider_name}.")
