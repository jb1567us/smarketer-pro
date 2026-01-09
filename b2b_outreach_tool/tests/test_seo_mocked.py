import asyncio
import sys
import os
import json
from unittest.mock import MagicMock, AsyncMock

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.seo_agent import SEOExpertAgent

async def test_seo_flow_mocked():
    print("🚀 Starting MOCKED SEO Flow Test...")
    
    # 1. Setup Mock Agent
    agent = SEOExpertAgent()
    
    # Mock hunt_backlinks to return fake targets instantly
    agent.hunt_backlinks = AsyncMock(return_value={
        "targets": [{"url": "http://blog1.com", "type": "Blog"}]
    })
    
    # Mock auto_submit_backlink to return success
    agent.auto_submit_backlink = AsyncMock(return_value={
        "status": "success", "method_used": "Web 2.0 AI Article (wordpress)"
    })
    
    # Mock design_link_wheel to return a simple 1-tier plan
    agent.design_link_wheel = MagicMock(return_value={
        "strategy_name": "Mock Wheel",
        "tiers": [{"level": 1, "properties": []}]
    })

    money_site = "https://mock-money.com"
    niche = "Automation"
    
    print(f"--- 🎡 Running MOCKED Link Wheel Mission for {niche} ---")
    results = await agent.run_link_wheel_mission(money_site, niche, strategy="standard")
    
    # 3. Verify Indexing Boost Calls
    print("\n✅ Indexing Boost Verification:")
    boost = results.get('indexing_boost', {})
    
    rss = boost.get('rss', {})
    print(f"RSS Pings: {len(rss.get('distribution_results', []))}")
    assert len(rss.get('distribution_results', [])) > 0
    
    bookmarks = boost.get('bookmarks', {})
    print(f"Bookmarks Processed for {len(bookmarks)} URLs.")
    assert len(bookmarks) > 0

    # 4. Verify successful_urls collection
    assert "http://blog1.com" in bookmarks

    print("\n✨ ALL MOCKED TESTS PASSED!")

if __name__ == "__main__":
    asyncio.run(test_seo_flow_mocked())
