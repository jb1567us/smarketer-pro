
import asyncio
import sys
import os
import aiohttp

sys.path.append(os.path.join(os.getcwd(), 'src'))
from scraper import search_searxng

async def test_live_dork():
    print("--- Testing Live Dork ---")
    dork = 'site:instagram.com "fitness" ("email" OR booking)'
    
    async with aiohttp.ClientSession() as session:
        # We need to simulate the config/engines
        # Researcher agent defaults: engines=['google', 'bing', 'yahoo']
        results = await search_searxng(dork, session, num_results=5, engines=['google', 'bing'])
        
    print(f"\nRESULTS Found: {len(results)}")
    for r in results:
        print(f" - {r['url']}")

if __name__ == "__main__":
    asyncio.run(test_live_dork())
