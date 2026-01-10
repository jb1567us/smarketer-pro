
import asyncio
from typing import Dict, List

# Copied logic for testing filtering
class TestInfluencerLogic:
    def _extract_handle(self, url: str, platform: str) -> str:
        """Extracts @handle from URL."""
        try:
            if platform in url:
                # Filter out reel/post URLs if they slip through
                if "/reel/" in url or "/p/" in url:
                    # Try to see if it's like instagram.com/user/reel/ID (rare)
                    # Usually it's instagram.com/reel/ID which has NO user info
                    return "Unknown"
                
                # Basic clean path extraction
                # e.g. https://www.instagram.com/michelle_lewin/ -> michelle_lewin
                parts = url.rstrip('/').split('/')
                potential_handle = parts[-1]
                
                # Ignore query params
                if "?" in potential_handle:
                    potential_handle = potential_handle.split('?')[0]
                    
                if potential_handle in ["reel", "p", "explore", "stories"]:
                    return "Unknown"
                    
                return f"@{potential_handle}"
        except:
            pass
        return "Unknown"

async def test_filtering():
    agent = TestInfluencerLogic()
    
    print("Checking URL Filtering...")
    
    good_url = "https://www.instagram.com/valid_user/"
    bad_reel = "https://www.instagram.com/reel/Cx12345/"
    bad_post = "https://www.instagram.com/p/Cy67890/"
    mixed_query = "https://www.instagram.com/valid_user?igshid=1234"
    
    h1 = agent._extract_handle(good_url, "instagram")
    h2 = agent._extract_handle(bad_reel, "instagram")
    h3 = agent._extract_handle(bad_post, "instagram")
    h4 = agent._extract_handle(mixed_query, "instagram")
    
    print(f"{good_url} -> {h1}")
    print(f"{bad_reel} -> {h2}")
    print(f"{bad_post} -> {h3}")
    print(f"{mixed_query} -> {h4}")
    
    assert h1 == "@valid_user"
    assert h2 == "Unknown"
    assert h3 == "Unknown"
    assert h4 == "@valid_user"
    
    print("\nSUCCESS: Filtering verified.")

if __name__ == "__main__":
    asyncio.run(test_filtering())
