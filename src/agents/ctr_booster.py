from .base import BaseAgent
from utils.browser_manager import BrowserManager
import asyncio
import random

class CTRBoosterAgent(BaseAgent):
    """
    Simulates real user search behavior to boost Click-Through Rate (CTR).
    Uses Playwright with stealth patterns.
    """
    def __init__(self, provider=None):
        super().__init__(
            role="CTR & Engagement Specialist",
            goal="Improve search rankings by simulating natural user interaction and clicks.",
            provider=provider
        )

    async def boost_keyword(self, keyword, target_domain, proxy=None, max_pages=5):
        """
        1. Search for keyword.
        2. Find target_domain in results.
        3. Click and stay on site.
        """
        browser_mgr = BrowserManager(session_id=f"ctr_{random.randint(1000, 9999)}")
        page = await browser_mgr.launch(headless=True, proxy=proxy)
        
        try:
            print(f"🚀 [CTR] Starting boost for '{keyword}' -> {target_domain}")
            
            # 1. Search (Google)
            await page.goto("https://www.google.com/search?q=" + keyword.replace(" ", "+"))
            await page.wait_for_load_state("networkidle")
            
            found = False
            for p in range(max_pages):
                print(f"  [CTR] Checking page {p+1}...")
                
                # Look for links containing target_domain
                links = await page.get_by_role("link").all()
                for link in links:
                    href = await link.get_attribute("href")
                    if href and target_domain in href:
                        print(f"  ✅ [CTR] Found target at {href}. Clicking...")
                        await link.click()
                        await page.wait_for_load_state("networkidle")
                        found = True
                        break
                
                if found: break
                
                # Go to next page
                next_btn = page.get_by_label("Next page")
                if await next_btn.is_visible():
                    await next_btn.click()
                    await page.wait_for_load_state("networkidle")
                else:
                    break
            
            if found:
                # 2. Simulate Engagement
                stay_time = random.randint(30, 120)
                print(f"  [CTR] Engaging for {stay_time} seconds...")
                
                # Random scrolling
                for _ in range(random.randint(3, 7)):
                    await page.mouse.wheel(0, random.randint(300, 800))
                    await asyncio.sleep(random.randint(2, 5))
                
                await asyncio.sleep(stay_time)
                return {"status": "success", "keyword": keyword, "domain": target_domain, "stay_time": stay_time}
            else:
                return {"status": "failed", "reason": "Target domain not found in top search results."}
                
        except Exception as e:
            return {"status": "error", "reason": str(e)}
        finally:
            await browser_mgr.close()

    def think(self, context):
        # Synchronous summary or planning
        pass
