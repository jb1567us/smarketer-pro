import sys
import os
import argparse
import asyncio
import time
from datetime import datetime

# Find path to src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from proxy_manager import proxy_manager
from config import config

async def run_worker(verbose=False, force=False):
    print(f"[{datetime.now()}] 🛡️ Proxy Background Worker starting...")
    if verbose: print("Arguments: verbose=True, force=" + str(force))
    print(f"[{datetime.now()}] 📅 Policy: Rotate pool every {config.get('proxies', {}).get('max_age_hours', 4)} hours.")
    
    # files to watch
    watched_files = {
        os.path.abspath(__file__): os.path.getmtime(__file__),
        os.path.abspath(os.path.join(os.path.dirname(__file__), 'proxy_manager.py')): os.path.getmtime(os.path.join(os.path.dirname(__file__), 'proxy_manager.py')),
        os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.py')): os.path.getmtime(os.path.join(os.path.dirname(__file__), 'config.py'))
    }

    print(f"[{datetime.now()}] 👁️  Watching for code changes...")

    while True:
        try:
            # Check for file changes
            for fpath, mtime in watched_files.items():
                if os.path.exists(fpath):
                    current_mtime = os.path.getmtime(fpath)
                    if current_mtime > mtime:
                        print(f"\n[{datetime.now()}] ♻️  Code change detected in {os.path.basename(fpath)}. Restarting worker...")
                        # Restart the script
                        os.execv(sys.executable, [sys.executable] + sys.argv)

            # We use force=False so it only rotates if the 15min timer is up
            # or if the pool is dangerously low.
            # [USER REQUEST] Target 1000 proxies (200 Elite + 800 Standard)
            # [USER REQUEST] Re-test every 5 minutes (5/60 = 0.0833 hours)
            await proxy_manager.ensure_fresh_proxies(min_count=1000, max_age_hours=0.0833, force=force, verbose=verbose)
            
            # Reset force after first run so we don't spam harvests in the loop
            force = False
            
            # --- Source Harvesting (Daily) ---
            from database import get_setting, save_setting
            last_source_harvest = int(get_setting('last_source_harvest_time', 0))
            if (time.time() - last_source_harvest) > 86400: # 24 hours
                 print(f"[{datetime.now()}] 🚜 Running Daily Proxy Source Harvest...")
                 from proxy_source_harvester import ProxySourceHarvester
                 harvester = ProxySourceHarvester()
                 # Run in executor to avoid blocking async loop
                 await asyncio.to_thread(harvester.harvest)
                 save_setting('last_source_harvest_time', int(time.time()))
                 
        except Exception as e:
            print(f"[{datetime.now()}] ⚠️ Error in worker loop: {e}")
        
        # [USER REQUEST] Continuous Mode: 10s loop (effectively continuously topping up)
        await asyncio.sleep(10)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Background Proxy Worker")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--force", action="store_true", help="Force a harvest regardless of freshness")
    args = parser.parse_args()

    # Pass args to worker
    config['worker_verbose'] = args.verbose
    config['worker_force'] = args.force

    try:
        if sys.platform == 'win32':
             asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(run_worker(verbose=args.verbose, force=args.force))
    except KeyboardInterrupt:
        print("\n🛑 Worker stopped by user.")
