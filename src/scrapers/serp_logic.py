from bs4 import BeautifulSoup
from typing import List, Dict

def extract_serp_results(html_content: str, engine: str = 'google') -> List[Dict[str, str]]:
    """
    Pure function to extract search results from SERP HTML.
    Supports Google and DuckDuckGo.
    """
    results = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Get all links
    all_links = soup.find_all('a')
    
    for link in all_links:
        try:
            url = link.get('href')
            if not url:
                continue
            
            # Filter out internal engine links
            if engine == 'google':
                if 'google.' in url or not url.startswith('http'):
                    continue
            elif engine == 'ddg':
                if 'duckduckgo.com' in url or 'spreadprivacy.com' in url:
                    continue
                if not url.startswith('http'):
                    continue
            
            # Check for title
            title = link.get_text(strip=True)
            if not title or len(title) < 5:
                continue
                
            # Avoid duplicates in this batch
            if any(r['url'] == url for r in results):
                continue

            results.append({
                'title': title,
                'url': url
            })
            
        except Exception:
            continue
            
    return results
