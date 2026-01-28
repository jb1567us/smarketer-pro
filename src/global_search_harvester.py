import asyncio
import csv
import os
import time
import random
import traceback
from typing import List, Dict

# Internal Imports
from proxy_manager import ProxyManager
from search_providers.direct_browser import DirectBrowser
from config import config

class GlobalSearchHarvester:
    """
    Scalable harvester that runs multiple authentic browser sessions in parallel.
    Features:
    - Proxy Rotation (per session)
    - Session Persistence (cookies/history)
    - Concurrent Workers
    - Automatic Retry Logic
    """
    
    def __init__(self, input_csv: str = None, input_data: List[Dict] = None, 
                 output_csv: str = "data/harvested_results.csv", 
                 workers: int = None):
        self.input_csv = input_csv
        self.input_data = input_data or []
        self.output_csv = output_csv
        
        # Load default from config if not provided
        if workers is None:
             workers = config.get('project', {}).get('concurrency_settings', {}).get('paid', {}).get('search', 3)
             print(f"⚙️ [GlobalSearch] Using configured concurrency: {workers} workers")
             
        self.workers = workers
        self.proxy_manager = ProxyManager()
        self.queue = asyncio.Queue()
        self.results = []
        
        # Ensure data dir exists
        os.makedirs(os.path.dirname(self.output_csv), exist_ok=True)

    async def initialize(self):
        """Prepares the harvester (loads proxies, reads CSV)."""
        print("🌍 [GlobalSearch] Initializing Proxy Manager...")
        await self.proxy_manager.enable_proxies()
        await self.proxy_manager.ensure_fresh_proxies(min_count=50)
        
        # Read Input (CSV or Memory)
        count = 0
        
        if self.input_data:
            print(f"🧠 [GlobalSearch] Loading {len(self.input_data)} tasks from memory...")
            for row in self.input_data:
                await self.queue.put(row)
                count += 1
        elif self.input_csv and os.path.exists(self.input_csv):
            print(f"📂 [GlobalSearch] Reading links from {self.input_csv}...")
            with open(self.input_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    await self.queue.put(row)
                    count += 1
        else:
            print("❌ No input data or valid CSV provided.")
            return False
        
        print(f"🚀 [GlobalSearch] Queued {count} search tasks.")
        return True

    async def _worker(self, worker_id: int):
        """Individual worker loop."""
        print(f"👷 [Worker {worker_id}] Started.")
        
        while True:
            try:
                # Get a task (non-blocking if empty eventually)
                if self.queue.empty():
                    break
                    
                task = await self.queue.get()
                
                query = task.get('query')
                platform = task.get('platform', 'google')
                
                if not query:
                    self.queue.task_done()
                    continue

                # Track retries in the task dict
                retries = task.get('retries', 0)
                
                # 1. Get a Fresh Proxy
                proxy = self.proxy_manager.get_proxy(tier='standard') 
                
                if not proxy:
                    print(f"⚠️ [Worker {worker_id}] No proxies available! Waiting 10s...")
                    await asyncio.sleep(10)
                    await self.queue.put(task) # Re-queue
                    self.queue.task_done()
                    continue
                
                # 2. Assign a Persistent Session ID
                safe_proxy_name = proxy.replace("http://", "").replace(":", "_")
                session_id = f"worker_{worker_id}_{safe_proxy_name}"
                
                print(f"🔍 [Worker {worker_id}] Searching: '{query}' via {proxy} (Attempt {retries+1})...")
                
                # 3. Execute Search
                db = DirectBrowser(headless=True, session_id=session_id, proxy=proxy)
                
                try:
                    # Random delay before starting to de-sync workers
                    await asyncio.sleep(random.uniform(1, 4))
                    
                    param_limit = int(task.get('num_results', 10))
                    results = await db.search(query, num_results=param_limit, engine=platform)
                    
                    if results:
                        print(f"✅ [Worker {worker_id}] Found {len(results)} results for '{query}'")
                        self._save_results(results, task)
                        self.proxy_manager.report_result(proxy, success=True)
                    else:
                        print(f"⚠️ [Worker {worker_id}] Zero results (Block/Captcha). Retrying...")
                        self.proxy_manager.report_result(proxy, success=False)
                        
                        # RETRY LOGIC
                        if retries < 3:
                            task['retries'] = retries + 1
                            print(f"🔄 [Worker {worker_id}] Re-queueing '{query}' (Retry {task['retries']}/3)")
                            await self.queue.put(task)
                        else:
                            print(f"❌ [Worker {worker_id}] Max retries reached for '{query}'. Giving up.")
                        
                except Exception as e:
                    print(f"❌ [Worker {worker_id}] Error: {e}")
                    self.proxy_manager.report_result(proxy, success=False)
                    
                    if retries < 3:
                        task['retries'] = retries + 1
                        print(f"🔄 [Worker {worker_id}] Re-queueing due to crash '{query}' (Retry {task['retries']}/3)")
                        await self.queue.put(task)
                
                self.queue.task_done()
                
            except Exception as e:
                print(f"💣 [Worker {worker_id}] Critical Crash: {e}")
                break
                
        print(f"💤 [Worker {worker_id}] Finished.")

    def _save_results(self, results: List[Dict], original_task: Dict):
        """Append results to CSV immediately and memory."""
        file_exists = os.path.exists(self.output_csv)
        
        with open(self.output_csv, 'a', newline='', encoding='utf-8') as f:
            fields = ['query', 'platform', 'title', 'url', 'source', 'dork', 'keyword', 'location']
            writer = csv.DictWriter(f, fieldnames=fields)
            
            if not file_exists:
                writer.writeheader()
                
            for r in results:
                row = {
                    'query': original_task.get('query'),
                    'platform': original_task.get('platform'),
                    'title': r.get('title'),
                    'url': r.get('url'),
                    'source': r.get('source'),
                    'dork': original_task.get('dork'),
                    'keyword': original_task.get('keyword'),
                    'location': original_task.get('location')
                }
                writer.writerow(row)
                self.results.append(row)

    async def run(self):
        """Main execution flow."""
        if not await self.initialize():
            return

        tasks = []
        for i in range(self.workers):
            tasks.append(asyncio.create_task(self._worker(i+1)))
            
        await self.queue.join()
        
        # Wait for workers
        for t in tasks:
            await t

        print("\n🎉 [GlobalSearch] Harvest Complete!")
        return self.results

if __name__ == "__main__":
    # Simple CLI wrapper
    import argparse
    parser = argparse.ArgumentParser(description="Global Search Harvester")
    parser.add_argument("--workers", type=int, default=None, help="Number of concurrent browsers (Default: Auto-detect from config)")
    parser.add_argument("--input", type=str, default="data/generated_search_links.csv", help="Input CSV")
    args = parser.parse_args()
    
    harvester = GlobalSearchHarvester(input_csv=args.input, workers=args.workers)
    asyncio.run(harvester.run())
