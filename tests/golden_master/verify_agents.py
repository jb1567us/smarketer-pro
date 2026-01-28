import json
import os
import sys
import glob
import asyncio
from unittest.mock import MagicMock, patch

# Add project root and src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from llm.base import LLMProvider
from agents.influencer_agent import InfluencerAgent
from agents.manager import ManagerAgent
from agents.researcher import ResearcherAgent
from agents.copywriter import CopywriterAgent

# Mapping of agent names in snapshots to classes
AGENT_MAP = {
    "InfluencerAgent": InfluencerAgent,
    "ManagerAgent": ManagerAgent,
    "ResearcherAgent": ResearcherAgent,
    "CopywriterAgent": CopywriterAgent
}

class ReplayProvider(LLMProvider):
    def __init__(self, history):
        self.history = history
        self.cursor = 0

    def _get_next_response(self, prompt, expected_type):
        if self.cursor >= len(self.history):
            raise Exception("REPLAY_ERROR: History exhausted")
        record = self.history[self.cursor]
        self.cursor += 1
        return record['response']

    def generate_text(self, prompt, **kwargs): return self._get_next_response(prompt, "text")
    def generate_json(self, prompt, **kwargs): return self._get_next_response(prompt, "json")
    async def generate_text_async(self, prompt, **kwargs): return self._get_next_response(prompt, "text")
    async def generate_json_async(self, prompt, **kwargs): return self._get_next_response(prompt, "json")

async def mock_run_harvester(*args, **kwargs):
    return [{"url": "https://test.com", "title": "Test", "snippet": "Test"}]

async def mock_smart_scrape(*args, **kwargs):
    return {"extracted_stats": {"followers": "10K"}, "status": "success"}

async def verify_agent_snapshot(fpath):
    print(f"Processing {os.path.basename(fpath)}...", end=" ")
    with open(fpath, 'r', encoding='utf-8') as f:
        snap = json.load(f)
    agent_name = snap.get("agent")
    agent_class = AGENT_MAP.get(agent_name)
    if not agent_class:
        print(f"SKIP (Unknown agent: {agent_name})")
        return False
        
    replay_provider = ReplayProvider(snap['llm_history'])
    
    with patch("src.global_search_harvester.GlobalSearchHarvester.run", new=mock_run_harvester), \
         patch("src.social_scraper.SocialScraper.smart_scrape", new=mock_smart_scrape), \
         patch("scraper.search_searxng", new=mock_run_harvester), \
         patch("extractor.fetch_html", new=lambda *a,**k: asyncio.sleep(0, "<html></html>")), \
         patch("database.log_agent_decision", new=MagicMock()), \
         patch("database.add_lead", new=MagicMock(return_value="test_id")):
         
        agent = agent_class(provider=replay_provider)
        if agent_name == "InfluencerAgent":
            agent.harvester = MagicMock()
            agent.harvester.mass_harvest = mock_run_harvester

        try:
            try:
                output = await agent.think_async(snap['input_context'])
            except NotImplementedError:
                output = await asyncio.to_thread(agent.think, snap['input_context'])

            if output == snap['output']:
                print(" PASS")
                return True
            else:
                print(" FAIL (Output mismatch)")
                return False
        except Exception as e:
            print(f" ERROR: {e}")
            return False

async def main():
    snapshot_dir = "tests/golden_master/snapshots"
    files = glob.glob(os.path.join(snapshot_dir, "agent_*.json"))
    print(f"Found {len(files)} Agent snapshots.")
    passed = 0
    failed = 0
    for f in files:
        if await verify_agent_snapshot(f):
            passed += 1
        else:
            failed += 1
    print(f"\nResults: {passed} PASSED, {failed} FAILED.")
    if failed > 0: sys.exit(1)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
