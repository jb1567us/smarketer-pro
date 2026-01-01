import sys
import os
import asyncio
from unittest.mock import MagicMock, patch

sys.path.append(os.path.join(os.getcwd(), 'src'))

from workflow import run_outreach

async def verify_batch_flow():
    print("🧪 Verifying Batch Workflow...")
    
    # Mocks
    mock_urls = [
        "http://good-site.com", 
        "http://bad-site.com", 
        "http://excluded-site.com", # Should be filtered by scrape/enrich check
        "http://no-html.com"
    ]
    
    # Mock Scrape Results
    # 1. good-site: Has HTML + Email
    # 2. bad-site: Has HTML + Email but will fail analysis
    # 3. excluded-site: Has HTML but no Email (or some other failure)
    # 4. no-html: Scrape fails
    
    async def mock_search(*args, **kwargs):
        return mock_urls

    async def mock_scrape(session, url, log_func=None):
        if url == "http://no-html.com":
            return {'url': url, 'emails': [], 'html': None, 'error': "Failed"}
        
        emails = ["test@example.com"]
        if url == "http://excluded-site.com":
            emails = [] # No emails found
            
        return {
            'url': url,
            'emails': emails,
            'html': "<html><body>Content</body></html>",
            'tech_stack': ['React'],
            'error': None
        }

    async def mock_enrich(candidate, target_niche=None, icp_criteria=None, log_func=None):
        url = candidate['url']
        if url == "http://bad-site.com":
            return {
                **candidate,
                'rejected': True,
                'qualification_reason': "Bad fit"
            }
        
        return {
            **candidate,
            'rejected': False,
            'analysis': {'industry': 'Tech', 'confidence': 'High'},
            'qualification_score': 90
        }

    # Patch Everything
    with patch('workflow.search_searxng', side_effect=mock_search) as p_search, \
         patch('workflow.scrape_site', side_effect=mock_scrape) as p_scrape, \
         patch('workflow.enrich_lead', side_effect=mock_enrich) as p_enrich, \
         patch('workflow.add_lead', return_value=True) as p_db:
         
        # Run
        await run_outreach(
            keywords="test query", 
            profile_names="default", 
            target_niche="Tech",
            exclusions=["excluded-pattern"] # Add a pattern that doesn't match our mocks to test logic
        )
        
        print("\n--- Verification Report ---")
        
        # SEARCH
        if p_search.called:
            print("✅ Phase 1 (Search): Executed")
        else:
             print("❌ Phase 1 (Search): FAILED")

        # SCRAPE
        # We expect 4 calls (all URLs)
        if p_scrape.call_count == 4:
            print(f"✅ Phase 1 (Scrape): Processed {p_scrape.call_count} sites")
        else:
            print(f"❌ Phase 1 (Scrape): Expected 4, got {p_scrape.call_count}")

        # ENRICH
        # Candidates passed to enrich:
        # - good-site (html=yes)
        # - bad-site (html=yes)
        # - excluded-site (html=yes). Note: workflow logic currently adds to candidates if HTML exists.
        # - no-html (html=no) -> Skipped
        # So we expect 3 calls.
        if p_enrich.call_count == 3:
             print(f"✅ Phase 2 (Enrich): Processed {p_enrich.call_count} candidates")
        else:
             print(f"❌ Phase 2 (Enrich): Expected 3, got {p_enrich.call_count}")
             
        # DB SAVE
        # We expect ONLY 'good-site' and 'bad-site'? 
        # Wait, 'bad-site' is rejected by enrich.
        # 'excluded-site' has no emails, so saving logic might skip it (depends on workflow.py logic).
        # workflow.py: "if emails: add_lead..."
        # So:
        # - good-site: Not rejected, Has emails -> Save
        # - bad-site: Rejected -> Skip
        # - excluded-site: Not rejected, No emails -> Skip
        # - no-html: Skipped earlier.
        # Expected: 1 Save.
        
        if p_db.call_count == 1:
            print(f"✅ Phase 3 (Save): Saved {p_db.call_count} lead (Expected 1)")
        else:
            print(f"❌ Phase 3 (Save): Expected 1, got {p_db.call_calls}")

if __name__ == "__main__":
    asyncio.run(verify_batch_flow())
