"""
Integration tests for proxy pipeline: harvest -> validate -> save -> retrieve
"""
import pytest
import asyncio
from proxies.validator import ProxyValidator
from db.proxies import save_proxies, get_best_proxies, invalidate_proxy_cache

@pytest.fixture
def sample_proxy_data():
    """Sample validated proxy data."""
    return [
        {
            'address': '1.2.3.4:8080',
            'protocol': 'http',
            'anonymity': 'elite',
            'country': 'US',
            'latency': 150
        },
        {
            'address': '5.6.7.8:3128',
            'protocol': 'http',
            'anonymity': 'standard',
            'country': 'UK',
            'latency': 200
        }
    ]

def test_proxy_save_and_retrieve(sample_proxy_data):
    """Test saving proxies and retrieving them from cache."""
    # Clear cache first
    invalidate_proxy_cache()
    
    # Save proxies
    save_proxies(sample_proxy_data, reset=True)
    
    # Retrieve all
    results = get_best_proxies(limit=10)
    
    # Should have saved proxies
    assert len(results) >= 2
    
    # Verify data integrity
    addresses = [r['address'] for r in results]
    assert '1.2.3.4:8080' in addresses
    assert '5.6.7.8:3128' in addresses

def test_proxy_cache_after_save(sample_proxy_data):
    """Test that cache is invalidated after save."""
    invalidate_proxy_cache()
    
    # First retrieval (cache miss)
    save_proxies(sample_proxy_data, reset=True)
    results1 = get_best_proxies(limit=10)
    
    # Second retrieval (should be cached)
    results2 = get_best_proxies(limit=10)
    
    # Results should be identical (from cache)
    assert len(results1) == len(results2)
    
    # Add new proxy
    new_proxy = [{
        'address': '9.10.11.12:80',
        'protocol': 'http',
        'anonymity': 'elite',
        'country': 'DE',
        'latency': 100
    }]
    save_proxies(new_proxy)
    
    # Cache should be invalidated, new results should include new proxy
    results3 = get_best_proxies(limit=10)
    assert len(results3) > len(results1)

def test_proxy_tier_filtering(sample_proxy_data):
    """Test retrieving proxies by anonymity tier."""
    invalidate_proxy_cache()
    save_proxies(sample_proxy_data, reset=True)
    
    # Get only elite
    elite_proxies = get_best_proxies(limit=10, min_anonymity='elite')
    assert all(p['anonymity'] == 'elite' for p in elite_proxies)
    
    # Get only standard
    standard_proxies = get_best_proxies(limit=10, min_anonymity='standard')
    assert all(p['anonymity'] == 'standard' for p in standard_proxies)

@pytest.mark.asyncio
async def test_validator_stats_tracking():
    """Test that validator properly tracks validation stats."""
    validator = ProxyValidator()
    
    # Stats should start inactive
    assert validator.stats['is_active'] == False
    assert validator.stats['total'] == 0
    
    # After batch validation, stats should update
    # (This is a lightweight test - full validation would require network)
    proxies = ['1.2.3.4:8080', '5.6.7.8:3128']
    
    # We can't run actual validation without network, but we verify structure
    assert validator.stats is not None
    assert 'checked' in validator.stats
    assert 'found' in validator.stats
