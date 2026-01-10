import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from social_scraper import SocialScraper

async def test_optimized_scraper():
    print("Initializing Scraper...")
    scraper = SocialScraper()
    
    # Test 1: Active Profile (Direct URL) -> Should use Browser
    print("\n--- TEST 1: Active Profile (Browser Path) ---")
    url = "https://www.linkedin.com/company/google"
    res = await scraper.smart_scrape(url)
    print(f"Source: {res.get('source', 'Error')}")
    print(f"Title: {res.get('title', 'N/A')}")

    # Test 2: Handle only (requires Dork to construct/validate)
    print("\n--- TEST 2: Handle 'elonmusk' (Dork Path) ---")
    res2 = await scraper.smart_scrape("elonmusk", platform="twitter")
    print(f"Source: {res2.get('source', 'Error')}")
    
    # Clean up
    await scraper.close()

if __name__ == "__main__":
    asyncio.run(test_optimized_scraper())
