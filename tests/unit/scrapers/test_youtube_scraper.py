"""
Unit tests for YouTube scraper.
"""
import pytest
from scrapers.social.implementations import YouTubeScraper

def test_youtube_handle_url_construction():
    """Test YouTube @ handle URL construction."""
    scraper = YouTubeScraper()
    
    # Modern @handle format
    url = scraper.construct_url("@mkbhd")
    assert url == "https://youtube.com/@mkbhd"
    
    # Without @ prefix
    url = scraper.construct_url("mkbhd")
    assert url == "https://youtube.com/@mkbhd"

def test_youtube_channel_id_url_construction():
    """Test YouTube channel ID URL construction."""
    scraper = YouTubeScraper()
    
    # Channel ID format (starts with UC)
    url = scraper.construct_url("UCBJycsmduvYEL83R_U4JriQ")
    assert url == "https://youtube.com/channel/UCBJycsmduvYEL83R_U4JriQ"

def test_youtube_custom_url_construction():
    """Test YouTube custom /c/ URL construction."""
    scraper = YouTubeScraper()
    
    # Custom URL format
    url = scraper.construct_url("c/Google")
    assert url == "https://youtube.com/c/Google"
    
    # With /c/ in handle
    url = scraper.construct_url("/c/TED")
    assert url == "https://youtube.com/c/TED"
