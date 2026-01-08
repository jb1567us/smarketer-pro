import sys
import os
import asyncio
import aiohttp

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from extractor import fetch_html
from config import config

async def main():
    url = "https://texasteacupmorkies.com"
    print(f"Testing connectivity to: {url}")

    # Test 1: Direct aiohttp (No Proxy, Simple Headers)
    print("\n--- Test 1: Direct aiohttp ---")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                print(f"Status: {resp.status}")
                text = await resp.text()
                print(f"Content length: {len(text)}")
    except Exception as e:
        print(f"Direct connection failed: {e}")

    # Test 2: Using fetch_html (Uses codebase logic + Proxies if enabled)
    print("\n--- Test 2: fetch_html (Codebase Logic) ---")
    try:
        # potentially mock proxy_manager if needed, but let's try with current state
        async with aiohttp.ClientSession() as session:
            content = await fetch_html(session, url)
            if content:
                print(f"fetch_html success! Content length: {len(content)}")
            else:
                print("fetch_html returned None (Failed)")
    except Exception as e:
        print(f"fetch_html raised exception: {e}")

if __name__ == "__main__":
    asyncio.run(main())
