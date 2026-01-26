
import sys
import os
import asyncio
sys.path.append(os.path.join(os.getcwd(), 'src'))
from proxy_manager import proxy_manager

if __name__ == "__main__":
    print("Force disabling proxies...")
    asyncio.run(proxy_manager.disable_proxies())
    print("Proxies disabled and SearXNG restarted.")
