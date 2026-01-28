import sys
import asyncio
import os
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'src'))
# Mock config before importing proxy_manager if needed, but we'll trust the real one
from src.proxy_manager import ProxyManager

async def test_fix():
    pm = ProxyManager()
    
    # Force enable to trigger update logic
    args = {"proxies": {"enabled": True}}
    # We can't easily patch config object since it's imported from config module.
    # But ProxyManager reads config.
    
    # Let's just call update_searxng_config directly.
    # It reads self.enabled.
    
    print("Running update_searxng_config() 1st time...")
    pm.enabled = True
    await pm.update_searxng_config()
    
    # Read file size
    size_1 = os.path.getsize(r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml")
    print(f"Size after 1st update: {size_1}")
    
    print("Running update_searxng_config() 2nd time...")
    await pm.update_searxng_config()
    
    size_2 = os.path.getsize(r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml")
    print(f"Size after 2nd update: {size_2}")
    
    if abs(size_2 - size_1) < 100:
        print("PASS: File size is stable. Fix confirmed.")
    else:
        print(f"FAIL: File grew by {size_2 - size_1} bytes!")

if __name__ == "__main__":
    asyncio.run(test_fix())
