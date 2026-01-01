import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from proxy_manager import proxy_manager
from extractor import fetch_html
import aiohttp

async def verify_proxies():
    print("--- Verifying Proxy Manager ---")
    
    # 1. Fetch Proxies
    print("\n1. Fetching Proxies...")
    await proxy_manager.fetch_proxies()
    
    if not proxy_manager.proxies:
        print("❌ No proxies fetched. Check internet or source URL.")
        return
        
    print(f"✅ Fetched and verified {len(proxy_manager.proxies)} proxies.")
    print(f"Sample: {proxy_manager.proxies[:5]}")
    
    # 2. Test Get Proxy
    print("\n2. Testing get_proxy()...")
    proxy = proxy_manager.get_proxy()
    print(f"Got proxy: {proxy}")
    if proxy:
        print("✅ get_proxy() works.")
    else:
        print("❌ get_proxy() returned None.")
        
    # 3. Test Integration with fetch_html
    print("\n3. Testing fetch_html integration (simulating extraction)...")
    target_url = "http://httpbin.org/ip"
    
    async with aiohttp.ClientSession() as session:
        print(f"Fetching {target_url} via fetch_html...")
        html = await fetch_html(session, target_url)
        
        if html:
            print(f"✅ fetch_html Success! Response:\n{html}")
        else:
            print("❌ fetch_html returned None. Check compilation/proxy health.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_proxies())
