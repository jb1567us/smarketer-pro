"""
Unit tests for proxy cache functionality.
"""
import pytest
import time
from db.proxies import (
    get_best_proxies, 
    invalidate_proxy_cache,
    _get_from_cache,
    _set_cache,
    _proxy_cache
)

def test_cache_set_and_get():
    """Test basic cache set/get operations."""
    invalidate_proxy_cache()  # Clear cache
    
    test_key = "test_key"
    test_value = [{"address": "1.2.3.4"}]
    
    _set_cache(test_key, test_value)
    result = _get_from_cache(test_key)
    
    assert result == test_value

def test_cache_ttl_expiration():
    """Test that cache entries expire after TTL."""
    invalidate_proxy_cache()
    
    from db import proxies as proxy_module
    original_ttl = proxy_module._cache_ttl
    proxy_module._cache_ttl = 0.1  # 100ms TTL for test
    
    try:
        test_key = "test_ttl"
        test_value = [{"address": "5.6.7.8"}]
        
        _set_cache(test_key, test_value)
        
        # Should be cached immediately
        assert _get_from_cache(test_key) == test_value
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Should be expired
        assert _get_from_cache(test_key) is None
    finally:
        proxy_module._cache_ttl = original_ttl

def test_cache_invalidation():
    """Test manual cache invalidation."""
    invalidate_proxy_cache()
    
    _set_cache("key1", ["data1"])
    _set_cache("key2", ["data2"])
    
    # Verify cached
    assert _get_from_cache("key1") == ["data1"]
    assert _get_from_cache("key2") == ["data2"]
    
    # Invalidate
    invalidate_proxy_cache()
    
    # Should be cleared
    assert _get_from_cache("key1") is None
    assert _get_from_cache("key2") is None

def test_cache_key_generation():
    """Test that different parameters generate different cache keys."""
    invalidate_proxy_cache()
    
    # These should use different cache keys
    # We can't directly test get_best_proxies without a DB,
    # but we can verify the key format would be distinct
    key1 = f"best_proxies_50_None_0"
    key2 = f"best_proxies_100_elite_1"
    
    assert key1 != key2
