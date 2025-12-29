import aiohttp
from bs4 import BeautifulSoup
import urllib.parse
from config import config

async def search_searxng(query, session, num_results=20, categories=None, engines=None):
    """
    Uses local SearXNG instance to find URLs via HTML scraping asynchronously.
    """
    base_url = config["search"]["searxng_url"]
    params = {
        "q": query,
    }
    
    if categories:
        params["categories"] = ",".join(categories)
    if engines:
        params["engines"] = ",".join(engines)
        
    headers = {
        "User-Agent": config["extraction"]["user_agent"]
    }
    
    print(f"Searching SearXNG for: {query}")
    
    try:
        async with session.get(base_url, params=params, headers=headers) as response:
            if response.status != 200:
                print(f"SearXNG returned {response.status}")
                return []
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            
            # SearXNG results 
            for article in soup.select('article.result'):
                a_tag = article.find('a', href=True)
                if a_tag:
                    url = a_tag['href']
                    if url.startswith('http'):
                        links.append(url)
            
            unique_links = list(set(links))
            print(f"Found {len(unique_links)} links.")
            return unique_links[:num_results]
            
    except Exception as e:
        print(f"Error scraping SearXNG: {e}")
        return []
