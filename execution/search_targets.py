import asyncio
import aiohttp
import argparse
import json
import sys
import os
from bs4 import BeautifulSoup

# --- Configuration (Defaults) ---
SEARXNG_URL = os.getenv("SEARXNG_URL", "http://localhost:8081/search")

async def search_searxng(query, limit=50):
    params = {
        "q": query,
        "format": "html",
        "safesearch": 1
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    unique_links = {}
    page = 1
    
    async with aiohttp.ClientSession() as session:
        while len(unique_links) < limit:
            params["pageno"] = page
            try:
                async with session.get(SEARXNG_URL, params=params, headers=headers, timeout=10) as response:
                    if response.status != 200:
                        sys.stderr.write(f"Error: SearXNG returned {response.status}\n")
                        break
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    links_found = 0
                    for article in soup.select('article.result'):
                        a_tag = article.find('a', href=True)
                        if a_tag:
                            url = a_tag['href']
                            title = a_tag.get_text(strip=True)
                            if url not in unique_links and url.startswith("http"):
                                unique_links[url] = title
                                links_found += 1
                    
                    if links_found == 0:
                        break
                        
                    page += 1
                    if page > 50: break # Safety limit
            except Exception as e:
                sys.stderr.write(f"Search Exception: {e}\n")
                break
                
    return [{"url": u, "title": t} for u, t in unique_links.items()][:limit]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search Targets Wrapper")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", type=int, default=50, help="Max results")
    args = parser.parse_args()
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    results = asyncio.run(search_searxng(args.query, args.limit))
    print(json.dumps(results, indent=2))
