import sys
import os
import asyncio
import sqlite3

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from database import init_db, save_setting, get_setting, get_connection
from agents.influencer_agent import InfluencerAgent

def test_settings_persistence():
    print("Testing Settings Persistence...")
    init_db()
    
    # Save a setting
    save_setting("test_key", "test_value")
    
    # Retrieve it
    val = get_setting("test_key")
    assert val == "test_value", f"Expected 'test_value', got {val}"
    
    # Overwrite it
    save_setting("test_key", "new_value")
    val = get_setting("test_key")
    assert val == "new_value", f"Expected 'new_value', got {val}"
    
    # Test App Mode default
    mode = get_setting("app_mode", "B2B")
    print(f"Current App Mode: {mode}")
    
    print("✅ Settings Persistence Passed!")

async def test_influencer_agent():
    print("Testing Influencer Agent...")
    agent = InfluencerAgent()
    
    # Mock mass_harvest to avoid real scraping
    async def mock_harvest(footprint, num_results=10, status_callback=None):
        print(f"  [Mock] Harvesting for {footprint}...")
        return [
            {"url": "https://instagram.com/fitness_guru", "title": "Fitness Guru (@fitness_guru) • Instagram photos"},
            {"url": "https://instagram.com/yoga_master", "title": "Yoga Master | DM for Collab"},
            {"url": "https://random.com/blog", "title": "Random Blog"} 
        ]
    
    agent.mass_harvest = mock_harvest
    
    results = await agent.scout_influencers("fitness", "instagram", limit=5)
    
    print("Results:", results)
    
    assert len(results) >= 2, "Should have found at least 2 influencers"
    assert results[0]['handle'] == "@fitness_guru", "Handle extraction failed"
    assert results[0]['platform'] == "instagram"
    
    print("✅ Influencer Agent Passed!")

if __name__ == "__main__":
    test_settings_persistence()
    asyncio.run(test_influencer_agent())
