import sys
import os
import asyncio
import aiohttp
import json

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from agents.seo_agent import SEOExpertAgent

async def main():
    url = "https://texasteacupmorkies.com"
    print(f"Verifying fix for: {url}")

    agent = SEOExpertAgent()
    print("Running audit_site (which now includes fallback logic)...")
    
    # We don't need a full LLM provider for this test if we just want to check if it fetched content.
    # However, audit_site calls self.generate_json at the end. 
    # To avoid LLM errors/costs, we can mock generate_json or just expect it to fail at LLM step but SUCCEED at fetching.
    
    # Let's just monkeypatch generate_json to return dummy dict so we can see if audit_site returns success structure.
    agent.generate_json = lambda prompt: {"patched": True, "analysis": "Mock analysis"}
    
    try:
        result = await agent.audit_site(url)
        
        # Check if we got the "metrics" key, which is injected after successful fetch+parse
        if 'metrics' in result:
            print("\nSUCCESS: audit_site retrieved content!")
            print(f"Title found: {result['metrics'].get('title')}")
            print(f"H1 count: {result['metrics'].get('h1_count')}")
        else:
            print("\nFAILURE: result did not contain metrics (likely fetch failed)")
            print(json.dumps(result, indent=2))
            
    except Exception as e:
        print(f"Exception during verification: {e}")

if __name__ == "__main__":
    asyncio.run(main())
