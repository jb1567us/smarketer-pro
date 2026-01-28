"""
Integration tests for social scraper fallback mechanism.
"""
import pytest
from scrapers.social.base import BaseSocialScraper
from scrapers.social.utils import parse_social_stats

def test_platform_url_construction():
    """Test URL construction for each platform."""
    scraper = BaseSocialScraper()
    
    # Base class returns None (must be overridden)
    assert scraper.construct_url("testuser") is None

def test_stat_parser_integration():
    """Test that stat parser works with real-world snippets."""
    # Instagram format
    ig_text = "10.5K Followers, 234 Following, 456 Posts - Check out cool photos"
    stats = parse_social_stats(ig_text)
    
    assert stats is not None
    assert stats['followers'] == '10.5K'
    assert stats['following'] == '234'
    assert stats['posts'] == '456'
    
    # Twitter format
    tw_text = "Social media expert • 2.5M followers"
    stats = parse_social_stats(tw_text)
    
    assert stats is not None
    assert stats['followers'] == '2.5M'

def test_multi_format_parsing():
    """Test parsing various formats in sequence."""
    test_cases = [
        ("100K followers", '100K'),
        ("1.2M Followers", '1.2M'),
        ("500 followers", '500'),
        ("10K abonnés", '10K'),  # French
        ("2M seguidores", '2M'),  # Spanish
    ]
    
    for text, expected in test_cases:
        stats = parse_social_stats(text)
        assert stats is not None, f"Failed to parse: {text}"
        assert stats['followers'] == expected, f"Wrong value for: {text}"
