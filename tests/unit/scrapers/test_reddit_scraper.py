"""
Unit tests for Reddit scraper.
"""
import pytest
from scrapers.social.implementations import RedditScraper

def test_reddit_user_url_construction():
    """Test Reddit user URL construction."""
    scraper = RedditScraper()
    
    # Standard user handle
    url = scraper.construct_url("testuser")
    assert url == "https://reddit.com/user/testuser"
    
    # With @ prefix
    url = scraper.construct_url("@testuser")
    assert url == "https://reddit.com/user/testuser"
    
    # With u/ prefix
    url = scraper.construct_url("u/testuser")
    assert url == "https://reddit.com/user/testuser"

def test_reddit_subreddit_url_construction():
    """Test Reddit subreddit URL construction."""
    scraper = RedditScraper()
    
    # With r/ prefix
    url = scraper.construct_url("r/python")
    assert url == "https://reddit.com/r/python"
    
    # In URL format
    url = scraper.construct_url("/r/learnprogramming")
    assert url == "https://reddit.com/r/learnprogramming"
