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
    
    print(f"Searching SearXNG for: {query} (Target: {num_results})")
    
    unique_links = set()
    page = 1
    
    while len(unique_links) < num_results:
        params["pageno"] = page
        
        try:
            async with session.get(base_url, params=params, headers=headers) as response:
                if response.status != 200:
                    print(f"SearXNG returned {response.status} on page {page}")
                    break
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Check for "no results"
                if "No results found" in html:
                    print(f"No more results on page {page}.")
                    break

                links_on_page = 0
                # SearXNG results 
                for article in soup.select('article.result'):
                    a_tag = article.find('a', href=True)
                    if a_tag:
                        url = a_tag['href']
                        if url.startswith('http') and url not in unique_links:
                            unique_links.add(url)
                            links_on_page += 1
                
                print(f"Page {page}: Found {links_on_page} new links. Total unique: {len(unique_links)}")
                
                if links_on_page == 0:
                     print("Zero links extracted from this page (parsing issue or end of results).")
                     break

                page += 1
                if page > 10: # Safety break
                    break
                    
        except Exception as e:
            print(f"Error scraping SearXNG page {page}: {e}")
            break
            
    return list(unique_links)[:num_results]
            

