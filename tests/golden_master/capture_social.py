import json
import os
import sys

# Add project root and src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from social_scraper import parse_social_stats

def capture_social_parsing():
    print("Capturing Social Stats Parsing...")
    # These are real examples of descriptions containing follower counts
    inputs = [
        "10.5K Followers, 500 Following, 1M Likes - Yoga and Fitness Coach",
        "Over 1,000,000 subs on YouTube! Business inquiries: test@gmail.com",
        "250k followers | Tech & AI Enthusiast | Seattle based",
        "Follow for more! 12.3m followers on TikTok",
        "500 followers - Just starting out"
    ]
    
    results = []
    for inp in inputs:
        parsed = parse_social_stats(inp)
        results.append({"input": inp, "output": parsed})
        
    os.makedirs("tests/golden_master/snapshots", exist_ok=True)
    with open("tests/golden_master/snapshots/social_parsing.json", 'w', encoding='utf-8') as f:
        json.dump({"type": "social_parsing", "results": results}, f, indent=2)
    print("  Saved social_parsing.json")

def capture_social_html():
    print("Capturing Social HTML Extraction...")
    # Mocking different platform metadata
    samples = [
        {
            "platform": "instagram",
            "html_input": '<html><head><meta property="og:description" content="10.5K Followers, 500 Following, 1M Likes - Yoga Coach"></head></html>',
            "final_stats": {"followers": "10.5K"}
        },
        {
            "platform": "tiktok",
            "html_input": '<html><head><meta property="og:description" content="250k followers | Tech Enthusiast"></head></html>',
            "final_stats": {"followers": "250k"}
        }
    ]
    
    with open("tests/golden_master/snapshots/social_html.json", 'w', encoding='utf-8') as f:
        json.dump({"type": "social_html", "samples": samples}, f, indent=2)
    print("  Saved social_html.json")

if __name__ == "__main__":
    capture_social_parsing()
    capture_social_html()
