
import asyncio
import sys
import os
import json
sys.path.append(os.path.join(os.getcwd(), 'src'))
from agents.researcher import ResearcherAgent

class MockProvider:
    def generate_json(self, prompt, **kwargs):
        if "Technographics" in prompt:
            return {
                "linkedin_url": "https://linkedin.com/company/example",
                "twitter_url": None,
                "instagram_url": None,
                "intent_signals": ["Hiring developers"],
                "company_bio": "An example tech company.",
                "technographics": ["Shopify", "HubSpot", "Meta Pixel"]
            }
        return []

async def test_tech_detection():
    print("Testing Technographics Detection...")
    agent = ResearcherAgent(provider=MockProvider())
    
    # We mock fetch_html so it returns something
    # Since we can't easily mock global functions in this script without complex setups,
    # we'll just check if the enrich_lead_data method uses the technographics field.
    
    # NOTE: This is a structural test of the agent's logic
    res = await agent.enrich_lead_data("https://example.com")
    
    print("Enrichment Results:")
    print(json.dumps(res, indent=2))
    
    assert "technographics" in res
    assert "Shopify" in res["technographics"]
    print("✅ Technographics field present and populated in agent output.")

if __name__ == "__main__":
    asyncio.run(test_tech_detection())
