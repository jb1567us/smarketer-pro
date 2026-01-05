import asyncio
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))
from src.model_fetcher import scan_all_free_providers

if __name__ == "__main__":
    print("Testing async scan...")
    try:
        results = asyncio.run(scan_all_free_providers(status_callback=print))
        print(f"\nFinal Results: {len(results)} valid models found.")
        for r in results:
            print(f"- {r['provider']}/{r['model_name']}")
    except Exception as e:
        print(f"Error: {e}")
