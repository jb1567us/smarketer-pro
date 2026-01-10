import asyncio
import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.seo_agent import SEOExpertAgent

async def test_seo_flow():
    print("🚀 Starting SEO Flow Test...")
    agent = SEOExpertAgent()
    
    money_site = "https://example-money-site.com"
    niche = "AI Automation Tools"
    
    print(f"--- 🎡 Running Link Wheel Mission for {niche} ---")
    results = await agent.run_link_wheel_mission(money_site, niche, strategy="standard")
    
    # 1. Verify Plan
    print("\n✅ Plan Verification:")
    print(f"Strategy: {results.get('plan', {}).get('strategy_name')}")
    assert "strategy_name" in results['plan']
    
    # 2. Verify AI Article Integration
    print("\n✅ Execution Verification:")
    for tier in results.get('executions', []):
        print(f"Tier {tier['tier']} has {len(tier['submissions'])} submissions.")
        for sub in tier['submissions']:
            print(f"  - Target: {sub['target']} | Method: {sub['method']}")
            assert "AI Article" in sub['method'] or "Manual" in sub['method']

    # 3. Verify Indexing Boost
    print("\n✅ Indexing Boost Verification:")
    boost = results.get('indexing_boost', {})
    
    rss = boost.get('rss', {})
    print(f"RSS Feed Generated: {len(rss.get('feed_xml', ''))} bytes")
    print(f"RSS Pings: {len(rss.get('distribution_results', []))}")
    assert len(rss.get('distribution_results', [])) > 0
    
    bookmarks = boost.get('bookmarks', {})
    print(f"Bookmarks Processed for {len(bookmarks)} URLs.")
    assert len(bookmarks) > 0

    print("\n✨ ALL TESTS PASSED!")

if __name__ == "__main__":
    asyncio.run(test_seo_flow())
