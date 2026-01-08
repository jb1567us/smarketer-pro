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
        "format": "html"
    }
    
    if categories:
        params["categories"] = ",".join(categories)
    if engines:
        params["engines"] = ",".join(engines)
        
    headers = {
        "User-Agent": config["extraction"]["user_agent"]
    }
    
    print(f"Searching SearXNG for: {query} (Target: {num_results})")
    print(f"DEBUG: Scraper Params: {params}")
    
    unique_links = {}
    page = 1
    
    while len(unique_links) < num_results:
        params["pageno"] = page
        
        from proxy_manager import proxy_manager
        proxy = proxy_manager.get_proxy()
        
        # FIX: Do NOT use a proxy if connecting to a local instance
        if "localhost" in base_url or "127.0.0.1" in base_url:
            proxy = None

        import time
        start_time = time.time()
        try:
            async with session.get(base_url, params=params, headers=headers, proxy=proxy, timeout=15) as response:
                latency = time.time() - start_time
                if response.status == 200:
                    if proxy:
                        proxy_manager.report_result(proxy, success=True, latency=latency)
                elif response.status != 200:
                    print(f"SearXNG returned {response.status} on page {page} using proxy {proxy}")
                    if proxy:
                        proxy_manager.report_result(proxy, success=False)
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
                        title = a_tag.get_text(strip=True)
                        
                        if url.startswith('http') and url not in unique_links:
                            unique_links[url] = title
                            links_on_page += 1
                
                print(f"Page {page}: Found {links_on_page} new links. Total unique: {len(unique_links)}")
                
                if links_on_page == 0:
                     print("Zero links extracted from this page (parsing issue or end of results).")
                     print(f"DEBUG: HTML DUMP (First 500 chars):\n{html[:500]}")
                     if "captcha" in html.lower(): print("🚫 CAPTCHA DETECTED")
                     break

                page += 1
                if page > 500: # Increased from 10 to allow exhaustive scraping
                    print("Hit safety page limit (500). Stopping.")
                    break
                    
        except aiohttp.ClientConnectorError as e:
            if page == 1:
                # Critical: Cannot even start. Likely Docker is down.
                raise ConnectionError(f"Could not connect to SearXNG at {base_url}. Ensure Docker is running.") from e
            print(f"Connection lost during paging: {e}")
            break
        except Exception as e:
            print(f"Error scraping SearXNG page {page}: {e}")
            break
            
    # Return list of dicts
    results = [{"url": u, "title": t} for u, t in unique_links.items()]
    return results[:num_results]
            


async def get_keyword_suggestions(query, session, source="google"):
    """
    Fetches autocomplete suggestions from various sources.
    Sources: google, amazon, youtube, bing
    """
    source = source.lower()
    
    urls = {
        "google": f"http://suggestqueries.google.com/complete/search?client=firefox&q={urllib.parse.quote(query)}",
        "youtube": f"http://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q={urllib.parse.quote(query)}",
        "amazon": f"https://completion.amazon.com/search/complete?search-alias=aps&mkt=1&q={urllib.parse.quote(query)}",
        "bing": f"https://api.bing.com/osjson.aspx?query={urllib.parse.quote(query)}"
    }
    
    url = urls.get(source)
    if not url:
        return []
        
    try:
        async with session.get(url, timeout=5) as resp:
            if resp.status == 200:
                # Force JSON even if mimetype is wrong (google returns text/javascript)
                data = await resp.json(content_type=None)
                # Basic json format for most suggest APIs is [query, [suggestions, ...]]
                if isinstance(data, list) and len(data) > 1:
                    return data[1]
                elif isinstance(data, dict) and "suggestions" in data:
                    return [s.get("value") for s in data["suggestions"]]
    except Exception as e:
        print(f"Error fetching suggestions from {source}: {e}")
        
    return []
