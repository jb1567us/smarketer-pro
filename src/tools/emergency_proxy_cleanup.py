
import sys
import os
import asyncio
import aiohttp
import time

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from database import get_connection, update_proxy_health, get_best_proxies
from proxy_manager import proxy_manager

async def strict_verify(proxy):
    """
    Strictly verifies a proxy against Google AND DuckDuckGo.
    Must pass BOTH to be considered 'SearXNG Ready'.
    """
    url = f"http://{proxy}"
    timeout = aiohttp.ClientTimeout(total=5) # Tight timeout
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # 1. Check Google
            async with session.get("https://www.google.com", proxy=url, ssl=False) as resp:
                if resp.status != 200:
                    return False
            
            # 2. Check DuckDuckGo (since it's failing in logs)
            async with session.get("https://duckduckgo.com", proxy=url, ssl=False) as resp:
                if resp.status != 200:
                    return False
                    
            return True
    except:
        return False

async def main():
    print("🚑 Starting Emergency Proxy Cleanup...")
    
    # 1. Get all active proxies
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT address FROM proxies WHERE is_active = 1")
    all_proxies = [r[0] for r in c.fetchall()]
    conn.close()
    
    print(f"Found {len(all_proxies)} active proxies in DB.")
    
    if not all_proxies:
        print("No proxies in DB to verify.")
        return

    # 2. Verify them in parallel
    print("Verifying proxies strictly (Google + DDG)...")
    semaphore = asyncio.Semaphore(100) # 100 concurrent
    good_proxies = []
    
    async def check(p):
        async with semaphore:
            is_good = await strict_verify(p)
            # Update DB immediately
            update_proxy_health(p, success=is_good, latency=0.5 if is_good else 0)
            if is_good:
                good_proxies.append(p)
                print(f"✅ {p} Passed", flush=True)
            else:
                # Mark as inactive/failed
                print(f"❌ {p} Failed (Removed)", flush=True)

    await asyncio.gather(*(check(p) for p in all_proxies))
    
    print(f"Cleanup Complete. {len(good_proxies)} proxies survived.")
    
    # 3. Force Update SearXNG Config
    print("Updating SearXNG configuration...")
    # Temporarily force manager to use only what we found (if any)
    # The manager reads from DB, so it should pick up the updated stats/active status
    await proxy_manager.update_searxng_config()
    
    print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
