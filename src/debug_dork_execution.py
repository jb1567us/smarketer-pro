import asyncio
import aiohttp
from agents.influencer_agent import InfluencerAgent

async def debug_search():
    print("--- Final Validation Debug ---")
    agent = InfluencerAgent()
    
    # Test Parameters
    niche = "fitness"
    platform = "instagram"
    limit = 5
    
    # Run the Agent Logic
    print(f"\n[1] Calling scout_influencers(niche='{niche}', platform='{platform}')...")
    # This calls mass_harvest internally with the dorks and filtering
    results = await agent.scout_influencers(niche, platform=platform, limit=limit)
    
    print(f"\nFinal Results Count: {len(results)}")
    
    # Validate Domains
    valid_domains = ["instagram.com", "linktr.ee", "beacons.ai"] # samples
    
    for i, res in enumerate(results):
        url = res['url']
        print(f"[{i+1}] {url}")
        
        # Check if it passed the strict filter
        is_valid = False
        for d in valid_domains:
            if d in url:
                is_valid = True
                break
        
        if not is_valid:
             # It might be another valid one I missed in valid_domains list above, 
             # but let's see if we got generic blogs.
             print(f"    WARNING: Potential filtering fail? {url}")

if __name__ == "__main__":
    asyncio.run(debug_search())
