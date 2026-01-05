import asyncio
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))
from agents.researcher import ResearcherAgent
from agents.comment_agent import CommentAgent
from agents.seo_agent import SEOExpertAgent

async def test_seo_upgrade():
    print("--- 1. Testing Footprint Scraper ---")
    r_agent = ResearcherAgent()
    # Mocking or using a very simple query to avoid long waits
    footprint = '"powered by wordpress" test' 
    # Logic in mass_harvest uses _perform_search which calls searching. 
    # For a unit test, we might mock, but let's try a real call with limit=1 to verify structure.
    # Note: If no internet/proxy, this might fail or return empty.
    results = await r_agent.detect_platform("https://wordpress.org/news/")
    print(f"Platform Detection (WordPress): {results}")
    
    print("\n--- 2. Testing Comment Spinner ---")
    c_agent = CommentAgent()
    seed = "This is a great article about SEO tools."
    spun = await c_agent.spin_comment(seed, context="B2B Marketing")
    print(f"Original: {seed}")
    print(f"Spun: {spun}")
    
    print("\n--- 3. Testing SEO Router (Simulation) ---")
    seo_agent = SEOExpertAgent()
    # Test routing to "CommentAgent" logic
    res_blog = await seo_agent.auto_submit_backlink(
        target_url="https://example-blog.com/post/1", 
        money_site_url="https://mysaaS.com", 
        context="AI Tools"
    )
    print(f"Router Result (Blog): {res_blog.get('method_used')}")
    
    # Test routing to "SEOBridge" (Web 2.0)
    # This might actually try to call bridge, which checks credentials. 
    # We provided no credentials for 'wordpress', so it should fail gracefully or fallback.
    res_wp = await seo_agent.auto_submit_backlink(
        target_url="https://mywordpress.com", # Mock trigger for platform detection
        money_site_url="https://mysaaS.com",
        context="AI Tools"
    )
    # It might detect as 'wordpress' then fail credentials and potentially return error or fallback
    print(f"Router Result (WordPress): {res_wp.get('method_used')} | Status: {res_wp.get('status')}")

if __name__ == "__main__":
    asyncio.run(test_seo_upgrade())
