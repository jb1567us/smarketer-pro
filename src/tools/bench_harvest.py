import sys
import os
import asyncio
import time
from datetime import datetime

# Path setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from proxy_manager import proxy_manager
from config import config

async def benchmark():
    print(f"\n[BENCHMARK] 🚀 Starting Finite 400-Concurrency Test...")
    print(f"[BENCHMARK] Target: Verify 1000 proxies w/ 400 threads.")
    
    start_time = time.time()
    
    # Force a harvest regardless of current status
    # verbose=True ensures we see the live output
    await proxy_manager.ensure_fresh_proxies(min_count=1000, max_age_hours=0, force=True, verbose=True)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n[BENCHMARK] ✅ Test Complete.")
    print(f"[BENCHMARK] ⏱️ Duration: {duration:.2f} seconds")
    print(f"[BENCHMARK] 📈 Concurrency: {config.get('proxies', {}).get('harvest_concurrency', 'Unknown')}")

if __name__ == "__main__":
    # Ensure event loop policy for Windows if needed (though running in Docker/Linux usually)
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(benchmark())
