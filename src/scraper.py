import aiohttp
from bs4 import BeautifulSoup
import urllib.parse
from config import config

async def search_searxng(query, session, num_results=20, categories=None, engines=None):
    """
    [MODIFIED] Now uses DirectBrowser (Playwright) to perform searches, 
    bypassing the legacy Proxy/SearXNG infrastructure.
    """
    from search_providers.direct_browser import DirectBrowser
    
    # Instantiate the browser 
    # [NOTE] Must be headless=True for Docker compatibility unless X11 is configured.
    browser = DirectBrowser(headless=True)
    
    # Perform the search
    # Note: 'session', 'categories', 'engines' are ignored in this new direct mode
    results = await browser.search(query, num_results=num_results)
    
    return results

# --- LEGACY SEARCH FUNCTION (Commented Out for Reference) ---
# async def _legacy_search_searxng(query, session, num_results=20, categories=None, engines=None):
#    ... (Old SearXNG Logic) ...


def _is_blocked_response(html_content):
    """
    Detects if the response content is actually a block/suspension page
    served with a 200 OK status code (common with SearXNG).
    """
    if not html_content: return False
    
    markers = [
        "suspended_time",
        "Access denied",
        "HTTP error 403",
        "Too many requests",
        "Rate limit exceeded",
        "CAPTCHA",
        "Our systems have detected unusual traffic"
    ]
    
    for m in markers:
        if m in html_content:
            return True
            
    return False
            


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
