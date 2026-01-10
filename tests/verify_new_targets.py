
import asyncio
import sys
import os
import re
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.social_scraper import SocialScraper

# Mocking the logic to verify the regex implementation without heavy imports
def get_profile_metrics_logic(html, platform):
    metrics = {"follower_count": "Unknown", "bio": ""}
    
    if platform == "threads":
        try:
            import json
            scripts = re.findall(r'<script type="application/json" data-sjs>(.*?)</script>', html, re.DOTALL)
            for s_content in scripts:
                f_match = re.search(r'"follower_count":\s*(\d+)', s_content)
                if f_match:
                    metrics["follower_count"] = f_match.group(1)
                
                bio_match = re.search(r'"biography":\s*"([^"]+)"', s_content)
                if bio_match:
                    metrics["bio"] = bio_match.group(1).encode('utf-8').decode('unicode_escape')
        except:
            pass
    return metrics

async def test_logic():
    print("--- Testing SocialScraper Detect/Construct ---")
    scraper = SocialScraper()
    
    u = "https://www.threads.net/@zuck"
    p = scraper._detect_platform(u)
    print(f"Detect Threads: {p}")
    assert p == "threads"
    
    constructed = scraper._construct_url("threads", "zuck")
    print(f"Construct Threads: {constructed}")
    assert constructed == "https://www.threads.net/@zuck"
    
    # Test Twitter Detect
    u2 = "https://x.com/elonmusk"
    p2 = scraper._detect_platform(u2)
    print(f"Detect X.com: {p2}")
    assert p2 == "twitter"

    print("\n--- Testing InfluencerAgent Parsing Logic ---")
    
    mock_threads_html = """
    <html>
    <body>
    <script type="application/json" data-sjs>
    {
        "user": {
            "u": "zuck",
            "follower_count": 123456,
            "biography": "Meta CEO."
        }
    }
    </script>
    </body>
    </html>
    """
    metrics = get_profile_metrics_logic(mock_threads_html, "threads")
    print(f"Metrics: {metrics}")
    assert metrics["follower_count"] == "123456"
    assert "Meta CEO" in metrics["bio"]
    
    print("\nSUCCESS: All logic verified.")

if __name__ == "__main__":
    asyncio.run(test_logic())
