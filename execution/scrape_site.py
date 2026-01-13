import asyncio
import aiohttp
import argparse
import json
import sys
import re
import random
from bs4 import BeautifulSoup

# --- Logic from extractor.py ---

EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
IGNORED_EXT = ('.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.io', '.co') # Simplified

def get_random_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    return {"User-Agent": random.choice(user_agents)}

async def fetch_html(session, url):
    try:
        async with session.get(url, headers=get_random_headers(), timeout=15) as response:
            if response.status == 200:
                return await response.text(errors='ignore')
    except:
        return None
    return None

def extract_emails(text):
    return list(set(re.findall(EMAIL_REGEX, text)))

async def scrape_site(url):
    async with aiohttp.ClientSession() as session:
        html = await fetch_html(session, url)
        if not html:
            return {"url": url, "error": "Could not fetch"}
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove scripts and styles for cleaner content
        for script in soup(["script", "style"]):
            script.decompose()
            
        text_content = soup.get_text(separator=' ', strip=True)
        emails = extract_emails(html) # Search raw HTML for emails
        
        return {
            "url": url,
            "content": text_content[:10000], # Truncate for LLM
            "emails": emails
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL to scrape")
    args = parser.parse_args()
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    result = asyncio.run(scrape_site(args.url))
    print(json.dumps(result, indent=2))
