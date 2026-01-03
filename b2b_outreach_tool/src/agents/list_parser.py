from bs4 import BeautifulSoup
import urllib.parse
import re

class ListParser:
    def __init__(self):
        pass

    def is_listicle(self, title, url):
        """
        Heuristic check if a page is likely a listicle or directory.
        """
        triggers = [
            "best", "top", "guide", "list", "directory", "places", "near me", 
            "ranking", "review", "comparison", "recommendations", "firms", "agencies"
        ]
        title_lower = title.lower()
        url_lower = url.lower()
        
        # Check for listicle patterns in title or URL
        is_trigger_match = any(t in title_lower for t in triggers) or any(t in url_lower for t in triggers)
        
        # Avoid blocking actual business sites that happen to have "agency" in them
        # (e.g., "Top Marketing Agency in Austin" vs "Best Marketing Agencies")
        if "agenc" in title_lower and not any(t in title_lower for t in ["best", "top", "list", "firms"]):
            return False
            
        return is_trigger_match

    def extract_external_links(self, html, source_url, keywords):
        """
        Extracts external links that might be business websites.
        Filters out internal links and known platforms.
        """
        from config import config
        blocklist = config.get("blocklist", {}).get("domains", [])
        
        soup = BeautifulSoup(html, 'html.parser')
        source_domain = urllib.parse.urlparse(source_url).netloc
        
        candidates = set()
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            title = a.get_text(strip=True).lower()
            
            try:
                parsed = urllib.parse.urlparse(href)
                domain = parsed.netloc.lower()
                
                if parsed.scheme not in ('http', 'https'):
                    continue
                    
                if not domain or domain == source_domain:
                    continue
                
                # Strip 'www.' for consistency
                clean_domain = domain[4:] if domain.startswith('www.') else domain
                
                # Check blocklist
                if any(bl in domain for bl in blocklist):
                    continue
                
                # Stricter heuristic: business sites often have their own domain 
                # and are linked via "Visit Website", "Website", or the company name.
                # Listicles often link to other directory pages or ad networks.
                
                # Filter out clearly non-business patterns
                if any(x in domain for x in ['search', 'click', 'track', 'adsystem', 'doubleclick']):
                    continue
                
                # If we have keywords, prioritze links that look like business homepages
                if parsed.path in ('', '/', '/index.html', '/home'):
                     candidates.add(href)
                elif any(kw.lower() in title for kw in keywords):
                     candidates.add(href)
                elif "website" in title or "visit" in title:
                     candidates.add(href)
                     
            except:
                continue
                
        # Limit to reasonable number
        return list(candidates)[:50]
