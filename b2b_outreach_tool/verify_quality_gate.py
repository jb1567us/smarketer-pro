import sys
import os
import asyncio
from unittest.mock import MagicMock, patch

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from workflow import process_url
from analyzer import analyze_lead_qualification

# Mock data
MOCK_AGENCY_HTML = """
<html>
<body>
    <h1>Bob's Plumbing Marketing</h1>
    <p>We help plumbers get more leads. We are a specialized digital agency.</p>
</body>
</html>
"""

MOCK_SAAS_HTML = """
<html>
<body>
    <h1>PlumbSoft</h1>
    <p>Accounting software for plumbing businesses. $20/month. Cloud based.</p>
</body>
</html>
"""

async def test_quality_gate():
    print("🧪 Testing Quality Gate Logic...")
    
    # 1. Test Rejection (Agency trying to look for Software)
    icp_software = "Must be a software product company (SaaS). Must NOT be an agency or service provider."
    
    # We need to patch fetch_html to avoid real network calls
    # Note: workflow.py uses local import for fetch_html in some places or extractor.fetch_html, 
    # so we patch extractor.fetch_html to be safe.
    
    with patch('workflow.extract_emails_from_site', return_value={'test@example.com'}), \
         patch('extractor.fetch_html', return_value=MOCK_AGENCY_HTML), \
         patch('analyzer.LLMFactory.get_provider') as mock_provider:
        
        # Mock LLM response for Rejection
        mock_llm = MagicMock()
        mock_llm.generate_json.return_value = {"score": 10, "reason": "This is a marketing agency, not a software company."}
        mock_provider.return_value = mock_llm
        
        print("\n--- Test Case 1: Rejection ---")
        print(f"Input: Agency Website | Criteria: {icp_software}")
        
        # Mocking session as None is fine if fetch_html is mocked
        result = await process_url(None, "http://agency.com", icp_criteria=icp_software)
        
        if result.get('rejected'):
            print(f"✅ PASS: Lead Rejected correctly. Score: {result.get('qualification_score')}")
        else:
            print(f"❌ FAIL: Lead should have been rejected. Score: {result.get('qualification_score')}")

    # 2. Test Acceptance (SaaS matching SaaS)
    with patch('workflow.extract_emails_from_site', return_value={'test@example.com'}), \
         patch('extractor.fetch_html', return_value=MOCK_SAAS_HTML), \
         patch('analyzer.LLMFactory.get_provider') as mock_provider:
        
        # Mock LLM response for Acceptance
        mock_llm = MagicMock()
        mock_llm.generate_json.return_value = {"score": 95, "reason": "This is clearly a SaaS product for plumbers."}
        mock_provider.return_value = mock_llm
        
        print("\n--- Test Case 2: Acceptance ---")
        print(f"Input: SaaS Website | Criteria: {icp_software}")
        
        result = await process_url(None, "http://saas.com", icp_criteria=icp_software)
        
        if not result.get('rejected') and result.get('qualification_score') > 70:
            print(f"✅ PASS: Lead Accepted correctly. Score: {result.get('qualification_score')}")
        else:
            print(f"❌ FAIL: Lead should have been accepted. Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_quality_gate())
