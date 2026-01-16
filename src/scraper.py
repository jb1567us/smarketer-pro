import aiohttp
from bs4 import BeautifulSoup
import urllib.parse
from config import config

async def search_searxng(query, session, num_results=20, categories=None, engines=None):
    """
    Uses local SearXNG instance to find URLs via HTML scraping asynchronously.
    Includes fallback to public instances if local is down.
    """
    from search_router import search_router

    # Use Smart Router for candidates
    urls_to_try = search_router.get_candidates()

    params = {
        "q": query,
        "format": "html",
        "safesearch": config["search"].get("safe_search", 1)
    }
    if categories: params["categories"] = ",".join(categories)
    if engines: params["engines"] = ",".join(engines)
    headers = {"User-Agent": config["extraction"]["user_agent"]}
    
    print(f"Searching SearXNG for: {query} (Target: {num_results})")
    
    unique_links = {}
    page = 1
    current_base_url = None

    while len(unique_links) < num_results:
        params["pageno"] = page
        
        from proxy_manager import proxy_manager
        proxy = proxy_manager.get_proxy()

        html_content = None
        success_url = None

        # Try URLs from Router
        # If we already have a locked base_url (from page 1), try to prefer it, 
        # but if it fails, we should fall back to others for subsequent pages too if needed?
        # Typically session stickiness is good, but if page 2 fails, we might need to switch instance.
        
        # Re-fetch candidates if we don't have a locked one or if the locked one is not in the list (failed?)
        # For simplicity: Always try current_base_url first if it exists
        current_candidates = urls_to_try
        if current_base_url:
             current_candidates = [current_base_url] + [u for u in urls_to_try if u != current_base_url]

        for attempt_url in current_candidates:
            # Don't use proxy for localhost
            initial_proxy = proxy if "localhost" not in attempt_url and "127.0.0.1" not in attempt_url else None
            
            # Try with proxy first (if applicable), then direct as fallback
            connection_modes = [(initial_proxy, "proxy")]
            if initial_proxy:
                connection_modes.append((None, "direct"))
            
            url_success = False
            
            for current_proxy, mode in connection_modes:
                try:
                    async with session.get(attempt_url, params=params, headers=headers, proxy=current_proxy, timeout=15) as response:
                        if response.status == 200:
                            html_content = await response.text()
                            success_url = attempt_url
                            current_base_url = attempt_url # Lock on
                            search_router.report_success(attempt_url)
                            if current_proxy: proxy_manager.report_result(proxy, success=True)
                            url_success = True
                            break # Success!
                        elif response.status == 429:
                            print(f"SearXNG {attempt_url} [{mode}] Rate Limit (429).")
                            # If direct failed with 429, maybe don't report failure to router immediately, but we can't do much.
                            # If proxy failed, we'll try direct next loop.
                        else:
                             print(f"SearXNG {attempt_url} [{mode}] returned {response.status}")
                except Exception as e:
                    print(f"Connection failed to {attempt_url} [{mode}]: {e}")
                    # Only report failure to router if ALL modes fail for this URL? 
                    # Simpler to report failure if the *primary* attempt fails, or maybe just log it.
                    # For now, we just continue to 'direct' mode or next URL.
            
            if url_success:
                break
            
            # If we are here, both proxy and direct failed for this attempt_url
            search_router.report_failure(attempt_url, "FailedAllModes")
            continue # Try next URL
        
        if not html_content:
            print(f"CRITICAL: Could not fetch results from any SearXNG instance for page {page}.")
            if page == 1:
                # Mock result for debugging stability if everything fails
                return [{"url": "https://en.wikipedia.org/wiki/Dog", "title": "Dog - Wikipedia (Fallback)"}]
            break

        soup = BeautifulSoup(html_content, 'html.parser')
        
        if "No results found" in html_content:
            print(f"No more results on page {page}.")
            break

        links_on_page = 0
        results_containers = soup.select('article.result') or soup.select('.result') or soup.select('.res-container')
        
        for article in results_containers:
            a_tag = article.select_one('h3 a') or article.select_one('.result_header a') or article.find('a', href=True)
            if a_tag and a_tag.get('href'):
                url = a_tag['href']
                if url.startswith('/url?q='):
                    url = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get('q', [url])[0]
                
                title = a_tag.get_text(strip=True)
                if url.startswith('http') and url not in unique_links:
                    unique_links[url] = title
                    links_on_page += 1
        
        print(f"Page {page} ({success_url}): Found {links_on_page} new. Total: {len(unique_links)}")
        
        if links_on_page == 0:
             break

        page += 1
        if page > 50: break
            
    return [{"url": u, "title": t} for u, t in unique_links.items()][:num_results]
            


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
