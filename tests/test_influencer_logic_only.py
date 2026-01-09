
import asyncio
from typing import Dict, List

# Copied logic for testing without dependencies
class TestInfluencerLogic:
    def get_profile_metrics(self, html: str, platform: str) -> Dict:
        """Parses HTML to find follower counts."""
        metrics = {"follower_count": "Unknown"}
        
        import re
        
        if platform == "instagram":
            # Look for meta description: e.g. "10M Followers, 200 Following..."
            match = re.search(r'content="([^"]*?Followers[^"]*?)"', html, re.IGNORECASE)
            if match:
                content = match.group(1)
                # content looks like "X Followers, Y Following, Z Posts..."
                parts = content.split(',')
                for p in parts:
                    if "Followers" in p:
                         metrics["follower_count"] = p.strip().split(' ')[0]
                         
        elif platform in ["twitter", "x"]:
             # Often obscured in JS, but sometimes in meta
             # "X Followers"
             match = re.search(r'content="([^"]*?Followers[^"]*?)"', html, re.IGNORECASE)
             if match:
                 content = match.group(1)
                 metrics["follower_count"] = content.split(' ')[0] # Very rough

        # Fallback
        if metrics["follower_count"] == "Unknown":
            fallback = re.search(r'([\d.,KM]+)\s+Followers', html, re.IGNORECASE)
            if fallback:
                 metrics["follower_count"] = fallback.group(1)

        return metrics

    def harvest_audience_sample(self, html: str, platform: str) -> List[str]:
        audience = set()
        import re
        mentions = re.findall(r'@([a-zA-Z0-9_.]+)', html)
        junk = ['instagram', 'twitter', 'tiktok', 'youtube', 'home', 'login', 'support']
        for m in mentions:
            if len(m) > 3 and m.lower() not in junk:
                audience.add(f"@{m}")
        return list(audience)[:5]

async def test_logic():
    agent = TestInfluencerLogic()
    
    insta_html = """
    <html>
    <meta property="og:description" content="10K Followers, 200 Following, 500 Posts - See Instagram photos and videos from @testuser" />
    <body>
    <p>Some comments by @fan1 and @fan2.</p>
    </body>
    </html>
    """
    
    print("Checking Instagram...")
    metrics = agent.get_profile_metrics(insta_html, "instagram")
    audience = agent.harvest_audience_sample(insta_html, "instagram")
    print(metrics)
    print(audience)
    
    assert metrics["follower_count"] == "10K"
    assert "10K" in metrics["follower_count"]
    assert "@fan1" in audience
    
    print("\nSUCCESS: Logic verified.")

if __name__ == "__main__":
    asyncio.run(test_logic())
