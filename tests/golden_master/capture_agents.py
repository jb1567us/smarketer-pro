import asyncio
import os
import sys
import json
from typing import List, Dict, Any
from unittest.mock import MagicMock, patch

# Add project root and src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from llm.base import LLMProvider
from llm.factory import LLMFactory
from agents.influencer_agent import InfluencerAgent
from agents.manager import ManagerAgent
from agents.researcher import ResearcherAgent
from agents.copywriter import CopywriterAgent

class RecordingProvider(LLMProvider):
    def __init__(self, real_provider=None):
        self.real_provider = real_provider or LLMFactory.get_provider()
        self.history = []

    async def generate_text_async(self, prompt, **kwargs):
        resp = await self.real_provider.generate_text_async(prompt, **kwargs)
        self.history.append({"prompt": prompt, "response": resp, "type": "text", "kwargs": kwargs})
        return resp

    async def generate_json_async(self, prompt, **kwargs):
        resp = await self.real_provider.generate_json_async(prompt, **kwargs)
        self.history.append({"prompt": prompt, "response": resp, "type": "json", "kwargs": kwargs})
        return resp
        
    def generate_text(self, prompt, **kwargs):
        resp = self.real_provider.generate_text(prompt, **kwargs)
        self.history.append({"prompt": prompt, "response": resp, "type": "text", "kwargs": kwargs})
        return resp

    def generate_json(self, prompt, **kwargs):
        resp = self.real_provider.generate_json(prompt, **kwargs)
        self.history.append({"prompt": prompt, "response": resp, "type": "json", "kwargs": kwargs})
        return resp

async def mock_run_harvester(*args, **kwargs):
    return [{"url": "https://test.com", "title": "Test", "snippet": "Test"}]

async def mock_smart_scrape(*args, **kwargs):
    return {"extracted_stats": {"followers": "10K"}, "status": "success"}

async def capture_all_agents():
    # Registry of agents and tasks
    scenarios = [
        {"name": "InfluencerAgent", "class": InfluencerAgent, "task": "Find 5 yoga influencers in New York"},
        {"name": "ManagerAgent", "class": ManagerAgent, "task": "Find 10 leads for a new SEO agency."},
        {"name": "ResearcherAgent", "class": ResearcherAgent, "task": "What are the common pain points of CTOs?"},
        {"name": "CopywriterAgent", "class": CopywriterAgent, "task": "Draft a cold email for a lead gen tool."}
    ]

    os.makedirs("tests/golden_master/snapshots", exist_ok=True)

    with patch("src.global_search_harvester.GlobalSearchHarvester.run", new=mock_run_harvester), \
         patch("src.social_scraper.SocialScraper.smart_scrape", new=mock_smart_scrape), \
         patch("scraper.search_searxng", new=mock_run_harvester), \
         patch("extractor.fetch_html", new=lambda *a,**k: asyncio.sleep(0, "<html></html>")), \
         patch("database.log_agent_decision", new=MagicMock()), \
         patch("database.add_lead", new=MagicMock(return_value="test_id")):

        for scenario in scenarios:
            name = scenario["name"]
            task = scenario["task"]
            print(f"🧠 Capturing {name}...")
            
            provider = RecordingProvider()
            agent = scenario["class"](provider=provider)
            
            if name == "InfluencerAgent":
                agent.harvester = MagicMock()
                agent.harvester.mass_harvest = mock_run_harvester

            try:
                output = await agent.think_async(task)
                snapshot = {
                    "agent": name, "input_context": task, "llm_history": provider.history, "output": output, "type": "agent_decision"
                }
                path = os.path.join("tests/golden_master/snapshots", f"agent_{name.lower()}.json")
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(snapshot, f, indent=2)
                print(f"  💾 Saved: {path}")
            except Exception as e:
                print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(capture_all_agents())
