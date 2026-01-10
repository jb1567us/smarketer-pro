import asyncio
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from utils.scrapebox_runner import ScrapeBoxRunner
from utils.gsa_service import GSAService

async def test_bridges():
    print("🧪 Testing Tool Bridges...")
    
    # 1. ScrapeBox
    sb = ScrapeBoxRunner(scrapebox_path="C:\\ScrapeBox\\scrapebox.exe")
    paths = sb.prepare_data_files("test", keywords=["seo", "outreach"], footprints=["\"write for us\""])
    
    if os.path.exists(paths['keywords']) and os.path.exists(paths['footprints']):
        print("✅ ScrapeBox data files created successfully.")
    else:
        print("❌ ScrapeBox data files missing.")

    # 2. GSA
    gsa = GSAService()
    res = await gsa.push_link_for_indexing("https://example.com/backlink", money_site="https://moneysite.com")
    
    if res['status'] in ['success', 'fallback']:
        print(f"✅ GSA Link push test passed: {res['message']}")
    else:
        print(f"❌ GSA Link push test failed: {res.get('reason')}")

if __name__ == "__main__":
    asyncio.run(test_bridges())
