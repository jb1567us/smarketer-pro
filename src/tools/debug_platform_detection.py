import asyncio
import aiohttp
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from agents.researcher import ResearcherAgent
from extractor import fetch_html

async def debug_detection(url):
    print(f"--- Debugging {url} ---")
    async with aiohttp.ClientSession() as session:
        html = await fetch_html(session, url, timeout=10)
        if not html:
            print("Failed to fetch HTML")
            return
        
        print(f"HTML length: {len(html)}")
        # Check for common markers manually
        markers = ["wp-content", "wp-includes", "wp-json", "Joomla", "Drupal"]
        for m in markers:
            if m in html:
                print(f"Found marker: {m}")
            else:
                print(f"Marker NOT found: {m}")
        
        researcher = ResearcherAgent()
        platform = await researcher.detect_platform(url)
        print(f"Researcher Detection: {platform}")

async def main():
    await debug_detection("https://wordpress.org")
    await debug_detection("https://www.joomla.org")

if __name__ == "__main__":
    asyncio.run(main())
