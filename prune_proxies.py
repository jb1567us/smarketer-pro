import sys
import os
import time
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'src'))

from database import get_connection
from proxy_manager import ProxyManager
import asyncio

def prune_dead_proxies():
    """
    Removes proxies that have:
    1. High failure rate
    2. Long time since last success
    3. Low reliability score (if available)
    """
    print("🔌 Connecting to database...")
    conn = get_connection()
    c = conn.cursor()
    
    # 1. Count before
    c.execute("SELECT COUNT(*) FROM proxies")
    total_before = c.fetchone()[0]
    
    print(f"📊 Total proxies BEFORE prune: {total_before}")
    
    # 2. Prune logic:
    # - Fail count > 3 AND success_count < 1 (Never worked, failed many times)
    # - Fail count > 10 (Just bad)
    # - Latency > 10.0 (Too slow)
    
    print("✂️  Pruning bad proxies...")
    c.execute("DELETE FROM proxies WHERE fail_count > 3 AND success_count = 0")
    deleted_junk = c.rowcount
    
    c.execute("DELETE FROM proxies WHERE fail_count > 10")
    deleted_failed = c.rowcount
    
    # Reset stats for the rest to give them *one* more chance if they are "okay"
    # Or just leave them.
    
    conn.commit()
    
    c.execute("SELECT COUNT(*) FROM proxies")
    total_after = c.fetchone()[0]
    
    print(f"Trashed {deleted_junk} never-working proxies.")
    print(f"Trashed {deleted_failed} constantly-failing proxies.")
    print(f"📊 Total proxies AFTER prune: {total_after}")
    
    conn.close()
    
    if total_after < 50:
         print("⚠️  Proxy pool critical! Triggering harvest...")
         pm = ProxyManager()
         asyncio.run(pm.fetch_proxies(verbose=True))
    else:
        print("✅ Pool looks cleaner. Triggering SearXNG update...")
        pm = ProxyManager()
        asyncio.run(pm.update_searxng_config())

if __name__ == "__main__":
    prune_dead_proxies()
