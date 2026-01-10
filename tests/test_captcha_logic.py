
import asyncio
from unittest.mock import MagicMock, AsyncMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from extractor import fetch_html, get_random_headers

async def test_captcha_mitigation():
    print("Testing Anti-Bot Logic...")
    
    # 1. Test Header Generation
    headers = get_random_headers()
    print(f"Generated Headers: {headers}")
    assert "User-Agent" in headers
    assert "Accept-Language" in headers
    
    # 2. Test CAPTCHA Detection (Simulated)
    # We mock the session and response to return a CAPTCHA page
    
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text.return_value = "<html>Please complete this security check... turnstile ...</html>"
    
    mock_session = AsyncMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response
    
    # We also need to mock proxy_manager to avoid real calls
    import extractor
    extractor.proxy_manager = MagicMock()
    extractor.proxy_manager.enabled = True
    extractor.proxy_manager.get_proxy.return_value = "http://test-proxy:8080"
    
    result = await fetch_html(mock_session, "http://target.com")
    
    # Since it detects CAPTCHA, it should retry (we mock 2 retries in code)
    # And eventually return None if all fail
    # We want to verify that report_result(success=False) was called
    
    print(f"Result (should be None as it was blocked): {result}")
    
    # Check if failure was reported
    extractor.proxy_manager.report_result.assert_called_with("http://test-proxy:8080", success=False)
    
    print("SUCCESS: CAPTCHA detected and proxy failure reported.")

if __name__ == "__main__":
    asyncio.run(test_captcha_mitigation())
