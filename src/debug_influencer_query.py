
import asyncio
import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'src'))
from agents.influencer_agent import InfluencerAgent

async def debug_queries():
    print("--- Debugging InfluencerAgent Query Generation ---")
    agent = InfluencerAgent()
    
    # Mock mass_harvest to just print the query
    async def mock_harvest(footprint, num_results=10, **kwargs):
        print(f"\n[Generated Query]: {footprint}")
        return []
        
    agent.mass_harvest = mock_harvest
    
    # Context 1: Standard Niche
    print("\nCase 1: Standard 'fitness' niche")
    await agent.scout_influencers(niche="fitness", platform="instagram", limit=5)

    # Context 2: With City and Audience
    print("\nCase 2: 'fitness' niche + City='Austin' + Audience='moms'")
    await agent.scout_influencers(niche="fitness", platform="instagram", limit=5, city="Austin", audience="moms")
    
    # Context 3: Wrong Platform
    print("\nCase 3: Platform='twitter' fallback")
    await agent.scout_influencers(niche="fitness", platform="twitter", limit=5)

if __name__ == "__main__":
    asyncio.run(debug_queries())
