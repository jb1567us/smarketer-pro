"""
Unit tests for social media stats parsing.
"""
import pytest
from scrapers.social.utils import parse_social_stats

def test_parse_english_followers():
    """Test parsing English follower counts."""
    text = "105K Followers, 107 Following, 1,203 Posts"
    stats = parse_social_stats(text)
    
    assert stats is not None
    assert stats['followers'] == '105K'
    assert stats['following'] == '107'
    assert stats['posts'] == '1,203'

def test_parse_large_numbers():
    """Test parsing large follower counts with M."""
    text = "2.5M followers"
    stats = parse_social_stats(text)
    
    assert stats is not None
    assert stats['followers'] == '2.5M'

def test_parse_french():
    """Test parsing French text."""
    text = "10K abonnés"
    stats = parse_social_stats(text)
    
    assert stats is not None
    assert stats['followers'] == '10K'

def test_parse_german():
    """Test parsing German text."""
    text = "500 Folger"
    stats = parse_social_stats(text)
    
    assert stats is not None
    assert stats['followers'] == '500'

def test_parse_spanish():
    """Test parsing Spanish text."""
    text = "1.2M seguidores"
    stats = parse_social_stats(text)
    
    assert stats is not None
    assert stats['followers'] == '1.2M'

def test_parse_subscribers():
    """Test parsing subscriber counts (YouTube style)."""
    text = "500K Subscribers"
    stats = parse_social_stats(text)
    
    assert stats is not None
    assert stats['followers'] == '500K'

def test_parse_empty_input():
    """Test handling of empty input."""
    stats = parse_social_stats(None)
    assert stats is None
    
    stats = parse_social_stats("")
    assert stats is None

def test_parse_no_match():
    """Test handling of text without stats."""
    text = "This is just random text"
    stats = parse_social_stats(text)
    
    assert stats is None

def test_parse_partial_stats():
    """Test parsing when only followers are present."""
    text = "100K followers only"
    stats = parse_social_stats(text)
    
    assert stats is not None
    assert 'followers' in stats
    assert 'following' not in stats
    assert 'posts' not in stats
