import aiohttp
import asyncio
import socket

import time
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

try:
    from database import get_best_proxies
except ImportError:
    print("Could not import database. Run from project root.")
    sys.exit(1)

TOR_PROXY = "socks5://127.0.0.1:9050"
TARGET_URL = "https://html.duckduckgo.com/html/"
# TARGET_URL = "https://www.google.com/search?q=test" # Alternative

async def check_tor():
    print(f"Testing Tor Connection ({TOR_PROXY})...")
    try:
        async with aiohttp.ClientSession() as session:
            start = time.time()
            # Use httpbin to verify IP
            async with session.get("http://httpbin.org/ip", proxy=TOR_PROXY, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Tor Online! IP: {data['origin']} (Latency: {time.time()-start:.2f}s)")
                    return True
                else:
                    print(f"❌ Tor Error: Status {resp.status}")
    except Exception as e:
        print(f"❌ Tor Failed: {e}")
    return False

async def check_duckduckgo(proxy_url):
    print(f"Testing Proxy against DuckDuckGo: {proxy_url}")
    try:
        async with aiohttp.ClientSession() as session:
            start = time.time()
            # Emulate the POST request used by SearXNG
            data = {'q': 'test search'}
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            
            async with session.post(TARGET_URL, data=data, proxy=proxy_url, headers=headers, timeout=10, ssl=False) as resp:
                print(f"  Result: {resp.status}")
                if resp.status == 200:
                    print(f"  ✅ SUCCESS! (Latency: {time.time()-start:.2f}s)")
                    return True
                elif resp.status == 403:
                    print("  ❌ BLOCKED (403 Forbidden)")
                else:
                    print(f"  ⚠️ Status {resp.status}")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
    return False

async def main():
    print("=== PROXY & TOR DIAGNOSTIC ===")
    
    # 1. Test Tor
    tor_ok = await check_tor()
    
    # 2. Test Top 5 Proxies from DB
    print("\nfetching top 5 proxies from DB...")
    proxies = get_best_proxies(limit=5)
    if not proxies:
        print("No proxies found in DB.")
    else:
        for p in proxies:
            addr = p['address']
            if not addr.startswith("http"): addr = f"http://{addr}"
            await check_duckduckgo(addr)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
