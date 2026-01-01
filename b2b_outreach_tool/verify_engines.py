import asyncio
import aiohttp
import sys
import os
sys.path.append('src')

# Mock config slightly to avoid full load issues if any
# but we need the url
from config import config

async def test_params(name, params):
    print(f"\n--- Testing {name} ---")
    print(f"Params: {params}")
    async with aiohttp.ClientSession() as session:
        url = config['search']['searxng_url']
        headers = {"User-Agent": config["extraction"]["user_agent"]}
        try:
            async with session.get(url, params=params, headers=headers) as resp:
                print(f"Status: {resp.status}")
                text = await resp.text()
                if "No results found" in text:
                    print("Result: NO RESULTS FOUND")
                else:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(text, 'html.parser')
                    results = soup.select('article.result')
                    print(f"Result: {len(results)} items found")
                    if len(results) == 0:
                        print("HTML DUMP (500 chars):")
                        print(text[:500])
        except Exception as e:
            print(f"Error: {e}")

async def main():
    base_params = {
        "q": "marketing agencies in Austin",
        "format": "html"
    }

    # Test 1: Bing only
    p1 = base_params.copy()
    p1['engines'] = 'bing'
    await test_params("Bing Only", p1)

    # Test 2: DDG only
    p2 = base_params.copy()
    p2['engines'] = 'duckduckgo'
    await test_params("DDG Only", p2)

    # Test 3: Composite (The one failing in app)
    p3 = base_params.copy()
    p3['engines'] = 'bing,duckduckgo,yahoo' 
    p3['categories'] = 'general'
    await test_params("Composite (Prod)", p3)

if __name__ == "__main__":
    asyncio.run(main())
