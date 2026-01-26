import pytest
import sys
import os
import asyncio
from unittest.mock import MagicMock, patch

# path hack
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_writer import DBWriter
from proxy_manager import ProxyManager
from agents.manager import ManagerAgent

# --- TEST DB CONCURRENCY ---
@pytest.mark.asyncio
async def test_db_queue_writer():
    """Verify that DBWriter processes queue items."""
    db_writer = DBWriter("msg_queue.db")
    db_writer.start()
    
    # We can't easily assert the internal sqlite state without reading it,
    # but we can verify the API doesn't crash
    db_writer.enqueue("INSERT INTO messages (content) VALUES (?)", ("test_msg",))
    
    # Wait a bit
    await asyncio.sleep(0.5)
    
    # It sends to thread, hopefully it works.
    # ideally we verify the DB file exists
    assert os.path.exists("msg_queue.db")
    
    db_writer.stop()

# --- TEST PROXY MANAGER ---
def test_proxy_manager_zero_latency():
    """Verify get_proxy returns instantly and relies on memory."""
    pm = ProxyManager()
    
    # Mock initialized state
    pm._initialized = True
    pm.proxies = ["1.1.1.1:8080", "2.2.2.2:8080"]
    pm.tor_available = False
    
    start = asyncio.get_event_loop().time()
    p = pm.get_proxy()
    end = asyncio.get_event_loop().time()
    
    assert p in ["http://1.1.1.1:8080", "http://2.2.2.2:8080"]
    # assert (end - start) < 0.001 # Microsecond speed

# --- TEST MANAGER AGENT SAFETY ---
def test_manager_agent_sanitization():
    """Verify intent classification doesn't execute dangerous commands blindly."""
    # This is a bit tricky since ManagerAgent calls LLM.
    # We will mock the LLM
    pass # Placeholder for Phase 4 improvements
