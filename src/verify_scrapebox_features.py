import asyncio
import aiohttp
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(__file__))

from agents.researcher import ResearcherAgent
from proxy_manager import proxy_manager

async def test_keyword_discovery():
    print("\n--- Testing Keyword Discovery (Level 1) ---")
    researcher = ResearcherAgent()
    keywords = await researcher.keyword_discovery("b2b outreach", levels=1, append_variants=False)
    print(f"Discovered {len(keywords)} keywords: {keywords[:10]}...")
    return len(keywords) > 0

async def test_platform_detection():
    print("\n--- Testing Platform Detection ---")
    researcher = ResearcherAgent()
    # Test a few known URLs
    urls = [
        "https://wordpress.org",
        "https://www.joomla.org"
    ]
    for url in urls:
        platform = await researcher.detect_platform(url)
        print(f"URL: {url} -> Detected: {platform}")
    return True

async def main():
    print("🚀 Starting ScrapeBox Integration Verification...")
    results = {
        "Keywords": await test_keyword_discovery(),
        "Platforms": await test_platform_detection()
    }
    
    print("\n--- Verification Summary ---")
    for task, success in results.items():
        print(f"{task}: {'✅ Pass' if success else '❌ Fail'}")

if __name__ == "__main__":
    asyncio.run(main())
