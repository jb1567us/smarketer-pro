import unittest
import asyncio
import time
from backend.market_monitor import MarketMonitor
from backend.database import init_db, get_connection

class TestMarketMind(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_market_check_integration(self):
        # We need an event loop for async tests
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        monitor = MarketMonitor.get_instance()
        
        # Run check for a specific niche
        # Note: MarketMonitor mocks search results, uses real agent (via router)
        found = loop.run_until_complete(monitor.run_market_check("HVAC Services"))
        
        self.assertGreaterEqual(found, 0)
        
        # Verify persistence
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT headline, strategic_hook FROM market_events WHERE niche = 'HVAC Services' ORDER BY timestamp DESC LIMIT 1")
        row = c.fetchone()
        conn.close()
        
        if found > 0:
            self.assertIsNotNone(row)
            self.assertTrue(len(row[0]) > 5) # Headline exists
            self.assertTrue(len(row[1]) > 10) # Hook generated
        
        loop.close()

if __name__ == "__main__":
    unittest.main()
