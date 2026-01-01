import asyncio
import aiohttp
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))
from scraper import search_searxng
from config import config

# Force config to only use google maps for this test
config['search']['profiles']['default']['engines'] = ['google maps']

async def debug_engine(engine_name):
    print(f"\n--- Testing Engines: {engine_name} ---")
    
    # Update config in memory for this test
    # config['search']['profiles']['default']['engines'] = [engine_name]
    
    async with aiohttp.ClientSession() as session:
        base_url = config['search']['searxng_url']
        params = {
            "q": "marketing agencies in Austin",
            "categories": "general",
            "engines": "bing,duckduckgo,yahoo", # Mimic production
             # "format": "html" # Removed to match scraper.py
        }
        
        # Add headers to match scraper.py
        headers = {
            "User-Agent": config["extraction"]["user_agent"]
        }
        
        print(f"Fetching {base_url} with params {params}...")
        async with session.get(base_url, params=params, headers=headers) as resp:
            print(f"Status: {resp.status}")
            html = await resp.text()
            
            if "No results were found" in html:
                print(f"❌  'No results were found'.")
            else:
                print(f"✅  Response received.")
                # Check for parsing
                soup = BeautifulSoup(html, 'html.parser')
                count = len(soup.select('article.result'))
                print(f"    Parsable Articles: {count}")
                if count == 0:
                   print("    DUMPING HTML (Partial):")
                   print(html[:1000])

async def run_diagnostics():
    await debug_engine('composite_test')

if __name__ == "__main__":
    from bs4 import BeautifulSoup
    asyncio.run(run_diagnostics())
