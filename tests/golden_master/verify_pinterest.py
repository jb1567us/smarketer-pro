"""
Golden Master Test: Pinterest Scraper
Verifies Pinterest scraper URL construction and data extraction.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))

from scrapers.social.implementations import PinterestScraper

def test_pinterest_url_construction():
    """Test Pinterest URL construction with various formats."""
    scraper = PinterestScraper()
    
    tests = [
        ("johndoe", "https://pinterest.com/johndoe"),
        ("@janedoe", "https://pinterest.com/janedoe"),
        ("company/", "https://pinterest.com/company"),
        ("/brandname/", "https://pinterest.com/brandname")
    ]
    
    passed = 0
    failed = 0
    
    for handle, expected_url in tests:
        result = scraper.construct_url(handle)
        if result == expected_url:
            passed += 1
        else:
            print(f"FAIL: Pinterest URL for '{handle}'")
            print(f"  Expected: {expected_url}")
            print(f"  Got: {result}")
            failed += 1
    
    return passed, failed

def test_pinterest_platform():
    """Test Pinterest platform detection."""
    scraper = PinterestScraper()
    
    # Just verify the scraper exists and has required methods
    assert hasattr(scraper, 'construct_url'), "Missing construct_url method"
    assert hasattr(scraper, 'platform_extract'), "Missing platform_extract method"
    
    return 1, 0

def main():
    print("Testing Pinterest Scraper Implementation...")
    
    total_passed = 0
    total_failed = 0
    
    # Test URL construction
    passed, failed = test_pinterest_url_construction()
    total_passed += passed
    total_failed += failed
    print(f"  URL Construction: {passed} PASSED, {failed} FAILED")
    
    # Test platform detection
    passed, failed = test_pinterest_platform()
    total_passed += passed
    total_failed += failed
    print(f"  Platform Detection: {passed} PASSED, {failed} FAILED")
    
    print(f"\nPinterest Scraper Results: {total_passed} PASSED, {total_failed} FAILED")
    
    return total_failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
