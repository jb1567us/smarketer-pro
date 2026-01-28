import sys
import os
import asyncio

# Setup path to import src modules
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'src'))

from src.proxy_manager import ProxyManager

async def force_update():
    print("🚀 Forcing SearXNG config update with new limits...")
    pm = ProxyManager()
    
    # This will read the new config (max_proxies=500) and db (min_success_count=1)
    # and overwrite settings.yml
    success, msg = await pm.update_searxng_config()
    
    if success:
        print(f"✅ Success: {msg}")
    else:
        print(f"❌ Failed: {msg}")

if __name__ == "__main__":

    try:
        asyncio.run(force_update())
    except Exception as e:
        print(f"Error: {e}")
