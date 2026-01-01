from bs4 import BeautifulSoup
import urllib.parse
import re

class ListParser:
    def __init__(self):
        pass

    def is_listicle(self, title, url):
        """
        Heuristic check if a page is likely a listicle.
        """
        triggers = ["best", "top", "guide", "list", "directory", "places", "near me"]
        title_lower = title.lower()
        url_lower = url.lower()
        
        return any(t in title_lower for t in triggers) or \
               any(t in url_lower for t in triggers)

    def extract_external_links(self, html, source_url, keywords):
        """
        Extracts external links that might be business websites.
        Filters out internal links and known platforms (facebook, twitter, etc. handled by blocklist).
        """
        soup = BeautifulSoup(html, 'html.parser')
        source_domain = urllib.parse.urlparse(source_url).netloc
        
        candidates = set()
        
        # Improve this by looking for 'rel=nofollow' or specific containers?
        # For now, just grab all unique external links.
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            try:
                parsed = urllib.parse.urlparse(href)
                domain = parsed.netloc
                
                # Filter valid http/https
                if parsed.scheme not in ('http', 'https'):
                    continue
                    
                # Filter internal
                if domain == source_domain or domain == "":
                    continue
                
                # Filter common noise (social, big tech)
                if any(x in domain for x in ['facebook', 'twitter', 'instagram', 'linkedin', 'google', 'youtube', 'amazon', 'pinterest']):
                    continue
                    
                candidates.add(href)
            except:
                continue
                
        # Limit to reasonable number (e.g. a Top 10 list usually has 10-20 links)
        # We might grab footer links too, but the Qualifier Agent will filter them.
        return list(candidates)[:30]
