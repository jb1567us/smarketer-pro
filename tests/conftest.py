"""
Pytest configuration and shared fixtures for unit tests.
"""
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def mock_proxy_list():
    """Sample proxy list for testing."""
    return [
        "1.2.3.4:8080",
        "5.6.7.8:3128",
        "9.10.11.12:80"
    ]

@pytest.fixture
def sample_social_stats_text():
    """Sample text snippets with follower counts."""
    return {
        "instagram": "105K Followers, 107 Following, 1,203 Posts",
        "twitter": "2.5M followers",
        "french": "10K abonnés",
        "german": "500 Folger",
        "spanish": "1.2M seguidores"
    }
