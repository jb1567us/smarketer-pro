import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

os.environ["ENVIRONMENT"] = "cloud"

from workflow import run_outreach
from config import config
from search_router import search_router

async def main():
    query = "interior designers in Austin TX"
    limit = 20
    
    print(f"ENVIRONMENT: {os.environ.get('ENVIRONMENT')}")
    print(f"Candidates: {search_router.get_candidates()}")
    
    try:
        results = await run_outreach(
            query, 
            max_results=limit,
            status_callback=lambda m: print(f"  [Status] {m}")
        )
        print(f"\n✅ Task Completed! Found {len(results)} leads.")
    except Exception as e:
        print(f"\n❌ Task Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
