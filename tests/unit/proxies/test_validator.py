"""
Unit tests for proxy validator.
"""
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from proxies.validator import ProxyValidator

@pytest.mark.asyncio
async def test_validator_initialization():
    """Test validator initializes with correct stats."""
    validator = ProxyValidator()
    
    assert validator.stats is not None
    assert validator.stats['is_active'] == False
    assert validator.stats['total'] == 0

@pytest.mark.asyncio
async def test_elite_tier_cloudflare_detection():
    """Verify Cloudflare detection determines tier."""
    validator = ProxyValidator()
    
    # Mock session for non-Cloudflare response
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.headers = {"Server": "nginx"}
    
    # Setup async context manager
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)
    mock_session.head.return_value = mock_response
    
    tier = await validator._check_elite_tier(mock_session, "http://1.2.3.4:8080")
    
    # Should return 2 (elite) for non-Cloudflare
    assert tier == 2

@pytest.mark.asyncio
async def test_standard_tier_with_cloudflare():
    """Verify standard tier when Cloudflare is present."""
    validator = ProxyValidator()
    
    # Mock session for Cloudflare response  
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.headers = {"Server": "cloudflare"}
    
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)
    mock_session.head.return_value = mock_response
    
    tier = await validator._check_elite_tier(mock_session, "http://1.2.3.4:8080")
    
    # Should return 1 (standard) for Cloudflare
    assert tier == 1

@pytest.mark.asyncio  
async def test_elite_check_failure_returns_standard():
    """Verify failed elite check returns standard tier."""
    validator = ProxyValidator()
    
    # Mock session that raises exception
    mock_session = MagicMock()
    mock_session.head.side_effect = Exception("Connection failed")
    
    tier = await validator._check_elite_tier(mock_session, "http://1.2.3.4:8080")
    
    # Should return 1 (standard) on failure
    assert tier == 1
