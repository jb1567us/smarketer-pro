
import asyncio
from typing import Dict, List

# Copied logic for testing
class TestInfluencerLogic:
    def get_profile_metrics(self, html: str, platform: str) -> Dict:
        """Parses HTML to find follower counts and BIO."""
        metrics = {"follower_count": "Unknown", "bio": ""}
        
        import re
        
        if platform == "instagram":
            # Look for meta description
            match = re.search(r'content="([^"]*?Followers[^"]*?)"', html, re.IGNORECASE)
            if match:
                content = match.group(1)
                
                # Extract Stats
                parts = content.split(',')
                for p in parts:
                    if "Followers" in p:
                         metrics["follower_count"] = p.strip().split(' ')[0]
                
                # Extract Bio / Description part (usually after ' - ')
                if " - " in content:
                    bio_part = content.split(" - ")[-1]
                    if "See Instagram photos" not in bio_part:
                        metrics["bio"] = bio_part.strip()
            
            if not metrics["bio"]:
                 # Try og:title
                 title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html)
                 if title_match:
                     t_content = title_match.group(1)
                     if ": " in t_content:
                         metrics["bio"] = t_content.split(": ")[-1].strip("'\"")

        elif platform in ["twitter", "x"]:
             match = re.search(r'content="([^"]*?Followers[^"]*?)"', html, re.IGNORECASE)
             if match:
                 content = match.group(1)
                 metrics["follower_count"] = content.split(' ')[0] 
                 
             desc_match = re.search(r'<meta property="og:description" content="([^"]+)"', html)
             if desc_match:
                 metrics["bio"] = desc_match.group(1)

        return metrics

async def test_bio_extraction():
    agent = TestInfluencerLogic()
    
    # 1. Instagram with Bio in Description
    insta_html_1 = """
    <html>
    <meta property="og:description" content="10K Followers, 200 Following, 500 Posts - See Instagram photos and videos from User (@user)" />
    </html>
    """
    # Note: "See Instagram..." is filtered out, so bio should be empty or handle specific check
    # Wait, splitting by " - " gives "See Instagram photos..." which is filtered out.
    # So bio should be empty here unless we implement better parsing.
    # My logic: `if "See Instagram photos" not in bio_part: metrics["bio"] = bio_part`
    
    # 2. Instagram with Real Bio in Description
    insta_html_2 = """
    <html>
    <meta property="og:description" content="50K Followers, 10 Following, 100 Posts - Fitness Coach | Eat Clean | Train Hard" />
    </html>
    """
    
    # 3. Instagram with Bio in Title
    insta_html_3 = """
    <html>
    <meta property="og:title" content="Jane Doe (@janedoe) on Instagram: 'Travel Blogger & Photographer'" />
    <meta property="og:description" content="100K Followers..." />
    </html>
    """
    
    print("Testing Bio Extraction...")
    
    m1 = agent.get_profile_metrics(insta_html_1, "instagram") # Expect empty bio (generic text filtered)
    m2 = agent.get_profile_metrics(insta_html_2, "instagram") # Expect "Fitness Coach | Eat Clean | Train Hard"
    m3 = agent.get_profile_metrics(insta_html_3, "instagram") # Expect "Travel Blogger & Photographer"
    
    print(f"Case 1 (Generic): {m1['bio']}")
    print(f"Case 2 (Descr): {m2['bio']}")
    print(f"Case 3 (Title): {m3['bio']}")
    
    assert m1['bio'] == ""
    assert "Fitness Coach" in m2['bio']
    assert "Travel Blogger" in m3['bio']
    
    print("\nSUCCESS: Bio extraction verified.")

if __name__ == "__main__":
    asyncio.run(test_bio_extraction())
