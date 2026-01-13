import asyncio
import aiohttp
import re
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from config import config

EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
STRICT_BLOCKLIST = set(config["blocklist"]["usernames"])
IGNORED_EXT = tuple(config["extraction"]["ignored_extensions"])
DEEP_CRAWL_KEYWORDS = config["extraction"]["deep_crawl_keywords"]

from proxy_manager import proxy_manager

import random

def get_random_headers():
    """Generates realistic browser headers."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
    ]
    
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    }

async def fetch_html(session, url, timeout=10, use_proxy=True):
    """Async fetch of a URL using rotated proxies and anti-bot headers."""
    # Ralph-Style Resilience: Increase retries and rotate strategies on failure
    max_retries = 3 if (proxy_manager.enabled and use_proxy) else 2
    
    is_last_captcha = False
    for attempt in range(max_retries):
        if attempt > 0:
            delay = random.uniform(2.0, 5.0) * attempt
            await asyncio.sleep(delay)
        else:
            await asyncio.sleep(random.uniform(0.5, 1.5))
        
        proxy = proxy_manager.get_proxy() if use_proxy else None
        start_time = time.time()
        headers = get_random_headers()
        
        try:
            async with session.get(url, timeout=timeout, proxy=proxy, headers=headers) as response:
                latency = time.time() - start_time
                content = await response.text(errors='ignore')
                
                lower_content = content.lower()
                banned_signatures = [
                    "turnstile", "challenge-platform", "cf-challenge", 
                    "captcha-delivery", "human verification", 
                    "are you a human", "security check", "access denied"
                ]
                
                is_captcha = any(sig in lower_content for sig in banned_signatures)
                is_last_captcha = is_captcha
                
                if response.status == 200 and not is_captcha:
                    if proxy:
                        proxy_manager.report_result(proxy, success=True, latency=latency)
                    return content
                
                elif response.status in [403, 429, 503, 401] or is_captcha:
                    if proxy:
                        print(f"  [Extractor] Ralph-Retry: Block detected (Status: {response.status}, Proxy: {proxy}). Rotating strategy...")
                        proxy_manager.report_result(proxy, success=False)
                    continue
                else:
                    return None
                    
        except Exception as e:
            if proxy:
                proxy_manager.report_result(proxy, success=False)
            pass
            
    return "__CAPTCHA_BLOCKED__" if is_last_captcha else None

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

def detect_tech_stack(html):
    """Detects common technologies from HTML content."""
    stack = set()
    html_lower = html.lower()
    
    # CMS / Platforms
    if 'wp-content' in html_lower or 'wp-includes' in html_lower:
        stack.add('WordPress')
    if 'cdn.shopify.com' in html_lower or 'shopify.checkout' in html_lower:
        stack.add('Shopify')
    if 'static1.squarespace.com' in html_lower:
        stack.add('Squarespace')
    if 'wix.com' in html_lower or 'x-wix-' in html_lower:
        stack.add('Wix')
    if 'webflow' in html_lower:
        stack.add('Webflow')
        
    # Frameworks / Libs
    if 'react' in html_lower or 'data-reactid' in html_lower:
        stack.add('React')
    if '__next_data__' in html_lower:
        stack.add('Next.js')
    if 'vue' in html_lower or 'data-v-' in html_lower:
        stack.add('Vue.js')
    if 'jquery' in html_lower:
        stack.add('jQuery')
    if 'bootstrap' in html_lower:
        stack.add('Bootstrap')
    if 'tailwind' in html_lower:
        stack.add('Tailwind')
        
    # Analytics / Ads
    if 'ua-' in html_lower or 'googletagmanager' in html_lower:
        stack.add('Google Analytics')
    if 'facebook-pixel' in html_lower or 'fbq(' in html_lower:
        stack.add('Facebook Pixel')
    if 'hotjar' in html_lower:
        stack.add('Hotjar')
        
    return list(stack)

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
