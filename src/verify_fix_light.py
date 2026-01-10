import sys
import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from extractor import fetch_html

async def main():
    url = "https://texasteacupmorkies.com"
    print(f"Verifying fix for: {url}")

    async with aiohttp.ClientSession() as session:
        print("1. Attempting fetch with proxy (simulating failure)...")
        html = await fetch_html(session, url, use_proxy=True, timeout=5)
        
        if html:
            print("  Unexpected: Proxy fetch succeeded (maybe lucky proxy?)")
        else:
            print("  Confirmed: Proxy fetch failed (as expected).")

        print("2. Attempting fetch with use_proxy=False (simulating fallback)...")
        html = await fetch_html(session, url, use_proxy=False, timeout=10)
        
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.title.string.strip() if soup.title else "No Title"
            print(f"  SUCCESS: Direct fetch worked! Title: {title}")
        else:
            print("  FAILURE: Direct fetch also failed.")

if __name__ == "__main__":
    asyncio.run(main())
