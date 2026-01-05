import asyncio
import sys
import os
import aiohttp

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from scraper import search_searxng
from config import config

async def main():
    print(f"SearXNG URL: {config['search']['searxng_url']}")
    
    async with aiohttp.ClientSession() as session:
        results = await search_searxng("site:twitter.com cold email", session, num_results=5)
        
        print(f"\nFound {len(results)} results:")
        for r in results:
            print(f"Title: {r['title']}")
            print(f"URL: {r['url']}")
            print("-" * 20)

if __name__ == "__main__":
    asyncio.run(main())
