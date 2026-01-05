
import sys
import os
import asyncio
import json
sys.path.append(os.path.join(os.getcwd(), 'src'))
from agents.seo_agent import SEOExpertAgent

def test_link_wheel():
    print("Initializing SEO Expert Agent...")
    agent = SEOExpertAgent()
    
    money_site = "https://example-roofing.com"
    niche = "Roofing in Miami"
    
    print(f"Designing Link Wheel for {money_site}...")
    plan = agent.design_link_wheel(money_site, niche, strategy="standard")
    
    print("Plan received:")
    print(json.dumps(plan, indent=2))
    
    # Check for basic fields
    assert "money_site" in plan
    assert "tiers" in plan
    assert plan["money_site"] == money_site
    
    print("Link Wheel design test passed!")

if __name__ == "__main__":
    test_link_wheel()
