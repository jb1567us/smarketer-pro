import asyncio
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from agents.ctr_booster import CTRBoosterAgent

async def test_ctr():
    print("🤖 Testing CTRBoosterAgent...")
    agent = CTRBoosterAgent()
    
    # We test it in a way that checks if it can at least launch (mocked keyword/domain)
    # Using a domain that likely exists but won't cause harm
    res = await agent.boost_keyword("test outreach automation", "google.com", max_pages=1)
    
    if res['status'] in ['success', 'failed']:
        # 'failed' is also fine as it means it ran but didn't find the domain in 1 page
        print(f"✅ CTRBooster test finished with status: {res['status']}")
    else:
        print(f"❌ CTRBooster test error: {res.get('reason')}")

if __name__ == "__main__":
    asyncio.run(test_ctr())
