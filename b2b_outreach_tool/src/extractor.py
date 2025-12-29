import asyncio
import aiohttp
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from config import config

EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
STRICT_BLOCKLIST = set(config["blocklist"]["usernames"])
IGNORED_EXT = tuple(config["extraction"]["ignored_extensions"])
DEEP_CRAWL_KEYWORDS = config["extraction"]["deep_crawl_keywords"]

async def fetch_html(session, url, timeout=10):
    """Async fetch of a URL."""
    try:
        async with session.get(url, timeout=timeout) as response:
            if response.status == 200:
                # Use errors='ignore' to handle potential encoding issues
                return await response.text(errors='ignore')
    except Exception:
        pass
    return None

def extract_emails_from_text(text):
    """Regex extraction from text."""
    found = set()
    matches = re.findall(EMAIL_REGEX, text)
    for email in matches:
        email_lower = email.lower()
        if email_lower.endswith(IGNORED_EXT):
            continue
        username = email_lower.split('@')[0]
        if not any(blocked in username for blocked in STRICT_BLOCKLIST):
            found.add(email_lower)
    return found

def get_internal_links(soup, base_url):
    """Finds internal links that might contain contact info."""
    internal_links = set()
    domain = urlparse(base_url).netloc
    
    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        
        # Check if internal
        if parsed.netloc == domain:
            # Check keywords
            url_lower = full_url.lower()
            if any(kw in url_lower for kw in DEEP_CRAWL_KEYWORDS):
                internal_links.add(full_url)
                
    return internal_links

async def extract_emails_from_site(session, url):
    """
    Crawls the homepage and relevant subpages (depth 1) for emails.
    """
    print(f"Scanning {url}...")
    emails = set()
    visited = set()
    to_visit = {url}
    
    # Homepage first
    homepage_html = await fetch_html(session, url, config["extraction"]["timeout"])
    if not homepage_html:
        return set()
    
    visited.add(url)
    emails.update(extract_emails_from_text(homepage_html))
    
    # Find subpages
    soup = BeautifulSoup(homepage_html, 'html.parser')
    internal_links = get_internal_links(soup, url)
    
    # Filter out already visited (just in case)
    to_visit = internal_links - visited
    
    # Limit deep crawl to prevent explosion (max 5 subpages)
    to_visit_list = list(to_visit)[:5]
    
    if to_visit_list:
        print(f"  Deep crawling {len(to_visit_list)} pages: {to_visit_list}")
        # Fetch all subpages concurrently
        tasks = [fetch_html(session, link) for link in to_visit_list]
        results = await asyncio.gather(*tasks)
        # actually aiohttp.gather returns a list of results, so this is correct.
        
        for html in results:
            if html:
                emails.update(extract_emails_from_text(html))
                
    return emails
